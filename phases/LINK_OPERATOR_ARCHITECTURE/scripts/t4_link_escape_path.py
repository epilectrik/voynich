"""
T4: LINK in Escape/Recovery Paths

C802 showed HT clusters near LINK but NOT near FL.
C796 showed HT correlates with escape rate at folio level.

Does LINK mediate the relationship between HT and escape?
- Is LINK near FL tokens?
- Is LINK density correlated with escape rate?
- Is LINK part of escape/recovery sequences?
"""

import json
import sys
sys.path.insert(0, 'C:/git/voynich')

from collections import Counter, defaultdict
from scripts.voynich import Transcript
from scipy import stats
import numpy as np

# Load class mapping
with open('C:/git/voynich/phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    class_data = json.load(f)

token_to_role = class_data['token_to_role']

def is_link(word):
    """LINK = token contains 'ol' substring (C609)"""
    return 'ol' in word.replace('*', '')

def is_fl(word, role_map):
    """FL = Flow Operator (escape/recovery)"""
    word = word.replace('*', '')
    return role_map.get(word, 'HT') == 'FLOW_OPERATOR'

def is_ht(word, role_map):
    """HT = not in 49-class grammar"""
    word = word.replace('*', '')
    return role_map.get(word, 'HT') == 'HT'

# Load transcript
tx = Transcript()
b_tokens = list(tx.currier_b())

# Group by folio and line
lines = defaultdict(list)
for t in b_tokens:
    key = (t.folio, t.line)
    lines[key].append(t)

print(f"Total B tokens: {len(b_tokens)}")
print(f"Total lines: {len(lines)}")

# Count FL tokens
fl_count = sum(1 for t in b_tokens if is_fl(t.word, token_to_role))
print(f"FL tokens: {fl_count} ({100*fl_count/len(b_tokens):.1f}%)")

# Distance analysis: LINK to FL
link_to_fl_distances = []
nonlink_to_fl_distances = []

for key, tokens in lines.items():
    # Find FL positions in this line
    fl_positions = []
    for i, t in enumerate(tokens):
        word = t.word.replace('*', '')
        if word.strip() and is_fl(word, token_to_role):
            fl_positions.append(i)

    if not fl_positions:
        continue

    # Calculate distances
    for i, t in enumerate(tokens):
        word = t.word.replace('*', '')
        if not word.strip():
            continue

        min_dist = min(abs(i - fp) for fp in fl_positions)

        if is_link(word):
            link_to_fl_distances.append(min_dist)
        else:
            nonlink_to_fl_distances.append(min_dist)

print(f"\n{'='*60}")
print(f"LINK-FL DISTANCE ANALYSIS")
print(f"{'='*60}")
print(f"LINK tokens in lines with FL: {len(link_to_fl_distances)}")
print(f"Non-LINK tokens in lines with FL: {len(nonlink_to_fl_distances)}")

if link_to_fl_distances and nonlink_to_fl_distances:
    print(f"\nMean distance to FL:")
    print(f"  LINK tokens: {np.mean(link_to_fl_distances):.2f}")
    print(f"  Non-LINK tokens: {np.mean(nonlink_to_fl_distances):.2f}")

    u_stat, p_mw = stats.mannwhitneyu(link_to_fl_distances, nonlink_to_fl_distances, alternative='two-sided')
    print(f"\nMann-Whitney U: p={p_mw:.4f}")

    if np.mean(link_to_fl_distances) < np.mean(nonlink_to_fl_distances) and p_mw < 0.05:
        print(f"=> LINK is CLOSER to FL")
    elif np.mean(link_to_fl_distances) > np.mean(nonlink_to_fl_distances) and p_mw < 0.05:
        print(f"=> LINK is FARTHER from FL")
    else:
        print(f"=> LINK distance to FL is NOT different from baseline")

# Folio-level correlation: LINK% vs FL%
print(f"\n{'='*60}")
print(f"FOLIO-LEVEL LINK-FL CORRELATION")
print(f"{'='*60}")

folio_stats = defaultdict(lambda: {'total': 0, 'link': 0, 'fl': 0, 'ht': 0})
for t in b_tokens:
    word = t.word.replace('*', '')
    if not word.strip():
        continue

    folio_stats[t.folio]['total'] += 1
    if is_link(word):
        folio_stats[t.folio]['link'] += 1
    if is_fl(word, token_to_role):
        folio_stats[t.folio]['fl'] += 1
    if is_ht(word, token_to_role):
        folio_stats[t.folio]['ht'] += 1

# Calculate rates
folios = sorted(folio_stats.keys())
link_rates = []
fl_rates = []
ht_rates = []

for f in folios:
    s = folio_stats[f]
    if s['total'] > 0:
        link_rates.append(100 * s['link'] / s['total'])
        fl_rates.append(100 * s['fl'] / s['total'])
        ht_rates.append(100 * s['ht'] / s['total'])

link_rates = np.array(link_rates)
fl_rates = np.array(fl_rates)
ht_rates = np.array(ht_rates)

# LINK vs FL
rho_link_fl, p_link_fl = stats.spearmanr(link_rates, fl_rates)
print(f"LINK% vs FL%: rho={rho_link_fl:.3f}, p={p_link_fl:.4f}")

# LINK vs HT
rho_link_ht, p_link_ht = stats.spearmanr(link_rates, ht_rates)
print(f"LINK% vs HT%: rho={rho_link_ht:.3f}, p={p_link_ht:.4f}")

# HT vs FL (for reference)
rho_ht_fl, p_ht_fl = stats.spearmanr(ht_rates, fl_rates)
print(f"HT% vs FL%: rho={rho_ht_fl:.3f}, p={p_ht_fl:.4f}")

# Transition sequence analysis: what comes before/after FL?
print(f"\n{'='*60}")
print(f"FL TRANSITION SEQUENCES")
print(f"{'='*60}")

pre_fl_link = 0
pre_fl_nonlink = 0
post_fl_link = 0
post_fl_nonlink = 0

for key, tokens in lines.items():
    for i, t in enumerate(tokens):
        word = t.word.replace('*', '')
        if not word.strip():
            continue

        if is_fl(word, token_to_role):
            # Check predecessor
            if i > 0:
                prev_word = tokens[i-1].word.replace('*', '')
                if prev_word.strip():
                    if is_link(prev_word):
                        pre_fl_link += 1
                    else:
                        pre_fl_nonlink += 1
            # Check successor
            if i < len(tokens) - 1:
                next_word = tokens[i+1].word.replace('*', '')
                if next_word.strip():
                    if is_link(next_word):
                        post_fl_link += 1
                    else:
                        post_fl_nonlink += 1

total_pre = pre_fl_link + pre_fl_nonlink
total_post = post_fl_link + post_fl_nonlink
baseline_link_rate = 13.2  # from C609

print(f"\nWhat precedes FL tokens?")
print(f"  LINK: {pre_fl_link}/{total_pre} = {100*pre_fl_link/total_pre:.1f}% (baseline: {baseline_link_rate:.1f}%)")

print(f"\nWhat follows FL tokens?")
print(f"  LINK: {post_fl_link}/{total_post} = {100*post_fl_link/total_post:.1f}% (baseline: {baseline_link_rate:.1f}%)")

# Enrichment ratios
pre_enrich = (pre_fl_link/total_pre) / (baseline_link_rate/100) if total_pre > 0 else 0
post_enrich = (post_fl_link/total_post) / (baseline_link_rate/100) if total_post > 0 else 0
print(f"\nEnrichment:")
print(f"  Pre-FL: {pre_enrich:.2f}x")
print(f"  Post-FL: {post_enrich:.2f}x")

# Summary
print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}")

findings = []
if link_to_fl_distances and nonlink_to_fl_distances:
    if p_mw < 0.05:
        if np.mean(link_to_fl_distances) < np.mean(nonlink_to_fl_distances):
            findings.append("LINK tokens are CLOSER to FL than non-LINK")
        else:
            findings.append("LINK tokens are FARTHER from FL than non-LINK")
    else:
        findings.append("LINK distance to FL is NOT different from baseline")

if p_link_fl < 0.05:
    if rho_link_fl > 0:
        findings.append(f"LINK% and FL% are POSITIVELY correlated (rho={rho_link_fl:.3f})")
    else:
        findings.append(f"LINK% and FL% are NEGATIVELY correlated (rho={rho_link_fl:.3f})")
else:
    findings.append("LINK% and FL% are NOT correlated at folio level")

for f in findings:
    print(f"- {f}")

print(f"\nInterpretation:")
if pre_enrich > 1.2 or post_enrich > 1.2:
    print(f"  LINK is enriched around FL tokens (escape context)")
else:
    print(f"  LINK is NOT particularly enriched around FL tokens")
