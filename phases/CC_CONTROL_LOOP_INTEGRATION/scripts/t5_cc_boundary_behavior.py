"""
T5: CC Boundary Behavior

Question: Does CC show LINK-like boundary enrichment?

C805 refuted C365 by showing LINK has boundary enrichment (17.2% first, 15.3% last vs 12.4% middle).
Test if CC shows similar pattern or is uniformly distributed.

Method:
1. Compute CC rates at first, middle, last positions
2. Compare to baseline and to LINK pattern
3. Test for boundary enrichment
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

CC_CLASSES = {10, 11, 12, 17}

# Collect tokens by line
line_tokens = defaultdict(list)
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    key = (token.folio, token.line)
    tc = token_to_class.get(w)

    is_cc = tc in CC_CLASSES
    is_link = 'ol' in w

    # CC subtypes
    cc_type = None
    if is_cc:
        if w == 'daiin':
            cc_type = 'DAIIN'
        elif w == 'ol':
            cc_type = 'OL'
        elif tc == 17:
            cc_type = 'OL_DERIVED'

    line_tokens[key].append({
        'word': w,
        'is_cc': is_cc,
        'is_link': is_link,
        'cc_type': cc_type,
    })

# Compute position rates
position_counts = {
    'CC': {'first': 0, 'middle': 0, 'last': 0, 'total': 0},
    'LINK': {'first': 0, 'middle': 0, 'last': 0, 'total': 0},
    'DAIIN': {'first': 0, 'middle': 0, 'last': 0, 'total': 0},
    'OL': {'first': 0, 'middle': 0, 'last': 0, 'total': 0},
    'OL_DERIVED': {'first': 0, 'middle': 0, 'last': 0, 'total': 0},
    'ALL': {'first': 0, 'middle': 0, 'last': 0, 'total': 0},
}

for key, tokens in line_tokens.items():
    n = len(tokens)
    if n < 3:  # Need at least 3 tokens for first/middle/last
        continue

    for i, t in enumerate(tokens):
        # Determine position
        if i == 0:
            pos = 'first'
        elif i == n - 1:
            pos = 'last'
        else:
            pos = 'middle'

        # Count
        position_counts['ALL'][pos] += 1
        position_counts['ALL']['total'] += 1

        if t['is_cc']:
            position_counts['CC'][pos] += 1
            position_counts['CC']['total'] += 1

        if t['is_link']:
            position_counts['LINK'][pos] += 1
            position_counts['LINK']['total'] += 1

        if t['cc_type']:
            position_counts[t['cc_type']][pos] += 1
            position_counts[t['cc_type']]['total'] += 1

print("=" * 60)
print("T5: CC BOUNDARY BEHAVIOR")
print("=" * 60)

# Compute rates and enrichments
baseline = {
    'first': position_counts['ALL']['first'] / position_counts['ALL']['total'],
    'middle': position_counts['ALL']['middle'] / position_counts['ALL']['total'],
    'last': position_counts['ALL']['last'] / position_counts['ALL']['total'],
}

print(f"\nBASELINE (all tokens, n={position_counts['ALL']['total']}):")
print(f"  First: {baseline['first']*100:.1f}%")
print(f"  Middle: {baseline['middle']*100:.1f}%")
print(f"  Last: {baseline['last']*100:.1f}%")

results = {}
for category in ['CC', 'LINK', 'DAIIN', 'OL', 'OL_DERIVED']:
    counts = position_counts[category]
    total = counts['total']
    if total < 50:
        continue

    rates = {
        'first': counts['first'] / total if total > 0 else 0,
        'middle': counts['middle'] / total if total > 0 else 0,
        'last': counts['last'] / total if total > 0 else 0,
    }

    # Boundary enrichment = (first + last) / (first + middle + last) compared to baseline
    boundary_rate = (counts['first'] + counts['last']) / total if total > 0 else 0
    baseline_boundary = baseline['first'] + baseline['last']
    boundary_enrichment = boundary_rate / baseline_boundary if baseline_boundary > 0 else 0

    # Chi-squared test against uniform
    observed = [counts['first'], counts['middle'], counts['last']]
    expected = [total * baseline['first'], total * baseline['middle'], total * baseline['last']]
    chi2, p = stats.chisquare(observed, expected)

    results[category] = {
        'total': total,
        'first': counts['first'],
        'middle': counts['middle'],
        'last': counts['last'],
        'first_rate': float(rates['first']),
        'middle_rate': float(rates['middle']),
        'last_rate': float(rates['last']),
        'boundary_rate': float(boundary_rate),
        'boundary_enrichment': float(boundary_enrichment),
        'chi2': float(chi2),
        'p': float(p),
    }

    print(f"\n{category} (n={total}):")
    print(f"  First: {counts['first']} ({rates['first']*100:.1f}%)")
    print(f"  Middle: {counts['middle']} ({rates['middle']*100:.1f}%)")
    print(f"  Last: {counts['last']} ({rates['last']*100:.1f}%)")
    print(f"  Boundary enrichment: {boundary_enrichment:.2f}x")
    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "NS"
    print(f"  Chi2={chi2:.2f}, p={p:.4f} {sig}")

# Compare CC to LINK
print("\n" + "=" * 60)
print("CC vs LINK COMPARISON:")
print("=" * 60)

if 'CC' in results and 'LINK' in results:
    cc = results['CC']
    link = results['LINK']

    print(f"\n                CC        LINK")
    print(f"  First:       {cc['first_rate']*100:5.1f}%    {link['first_rate']*100:5.1f}%")
    print(f"  Middle:      {cc['middle_rate']*100:5.1f}%    {link['middle_rate']*100:5.1f}%")
    print(f"  Last:        {cc['last_rate']*100:5.1f}%    {link['last_rate']*100:5.1f}%")
    print(f"  Boundary:    {cc['boundary_enrichment']:5.2f}x    {link['boundary_enrichment']:5.2f}x")

    # Are they similar?
    pattern_match = (
        (cc['first_rate'] > cc['middle_rate']) == (link['first_rate'] > link['middle_rate']) and
        (cc['last_rate'] > cc['middle_rate']) == (link['last_rate'] > link['middle_rate'])
    )
    print(f"\n  Pattern match (boundary > middle): {'YES' if pattern_match else 'NO'}")

# Subtype comparison
print("\n" + "-" * 40)
print("CC SUBTYPE COMPARISON:")
print("-" * 40)

for subtype in ['DAIIN', 'OL', 'OL_DERIVED']:
    if subtype in results:
        r = results[subtype]
        print(f"\n{subtype}:")
        print(f"  First: {r['first_rate']*100:.1f}%, Middle: {r['middle_rate']*100:.1f}%, Last: {r['last_rate']*100:.1f}%")
        if r['first_rate'] > r['middle_rate']:
            print(f"  -> INITIAL-BIASED")
        elif r['last_rate'] > r['middle_rate']:
            print(f"  -> FINAL-BIASED")
        else:
            print(f"  -> MIDDLE-CONCENTRATED")

# Save results
out_path = PROJECT_ROOT / 'phases' / 'CC_CONTROL_LOOP_INTEGRATION' / 'results' / 't5_boundary_behavior.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path.name}")
