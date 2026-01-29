"""
T1: LINK Transition Grammar Verification

LINK is defined as tokens containing 'ol' (C609: 13.2% of B, 3,047 tokens).

Verify C366 claims:
- LINK preceded by AUXILIARY (1.50x), FLOW_OPERATOR (1.30x)
- LINK followed by HIGH_IMPACT (2.70x), ENERGY_OPERATOR (1.15x)

Tests whether LINK truly marks grammar state transitions.
"""

import json
import sys
sys.path.insert(0, 'C:/git/voynich')

from collections import Counter, defaultdict
from scripts.voynich import Transcript
from scipy import stats

# Load class mapping for role identification
with open('C:/git/voynich/phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    class_data = json.load(f)

token_to_role = class_data['token_to_role']

def is_link(word):
    """LINK = token contains 'ol' substring (C609)"""
    return 'ol' in word.replace('*', '')

# Load transcript and build token sequences by line
tx = Transcript()
b_tokens = list(tx.currier_b())

# Group by folio and line
lines = defaultdict(list)
for t in b_tokens:
    key = (t.folio, t.line)
    lines[key].append(t)

print(f"Total B tokens: {len(b_tokens)}")
print(f"Total lines: {len(lines)}")

# Count LINK tokens
link_count = sum(1 for t in b_tokens if is_link(t.word))
print(f"LINK tokens ('ol' in word): {link_count} ({100*link_count/len(b_tokens):.1f}%)")

# Analyze transitions around LINK tokens
predecessor_roles = Counter()
successor_roles = Counter()
total_links_with_context = 0

# Baseline: what follows any token?
baseline_successor = Counter()
baseline_predecessor = Counter()
total_baseline = 0

for key, tokens in lines.items():
    for i, t in enumerate(tokens):
        word = t.word.replace('*', '')
        if not word.strip():
            continue

        role = token_to_role.get(word, 'HT')
        is_link_token = is_link(word)

        # For baseline (any token)
        if i > 0:
            prev_word = tokens[i-1].word.replace('*', '')
            if prev_word.strip():
                prev_role = token_to_role.get(prev_word, 'HT')
                baseline_predecessor[prev_role] += 1
        if i < len(tokens) - 1:
            next_word = tokens[i+1].word.replace('*', '')
            if next_word.strip():
                next_role = token_to_role.get(next_word, 'HT')
                baseline_successor[next_role] += 1
        total_baseline += 1

        if is_link_token:
            total_links_with_context += 1
            # Check predecessor
            if i > 0:
                prev_word = tokens[i-1].word.replace('*', '')
                if prev_word.strip():
                    prev_role = token_to_role.get(prev_word, 'HT')
                    predecessor_roles[prev_role] += 1

            # Check successor
            if i < len(tokens) - 1:
                next_word = tokens[i+1].word.replace('*', '')
                if next_word.strip():
                    next_role = token_to_role.get(next_word, 'HT')
                    successor_roles[next_role] += 1

print(f"\n{'='*60}")
print(f"LINK TRANSITION ANALYSIS")
print(f"{'='*60}")
print(f"LINK tokens with predecessors: {sum(predecessor_roles.values())}")
print(f"LINK tokens with successors: {sum(successor_roles.values())}")

# Calculate enrichment ratios
print(f"\n--- PREDECESSORS (what comes before LINK) ---")
total_predecessors = sum(predecessor_roles.values())
total_baseline_pred = sum(baseline_predecessor.values())

pred_enrichments = []
for role in sorted(set(predecessor_roles.keys()) | set(baseline_predecessor.keys())):
    link_rate = predecessor_roles.get(role, 0) / total_predecessors if total_predecessors > 0 else 0
    base_rate = baseline_predecessor.get(role, 0) / total_baseline_pred if total_baseline_pred > 0 else 0
    enrichment = link_rate / base_rate if base_rate > 0 else float('inf')
    pred_enrichments.append((role, predecessor_roles.get(role, 0), link_rate, base_rate, enrichment))

pred_enrichments.sort(key=lambda x: -x[4] if x[4] != float('inf') else -999)
print(f"{'Role':<20} {'Count':>8} {'LINK%':>8} {'Base%':>8} {'Enrich':>8}")
print(f"{'-'*20} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")
for role, count, link_rate, base_rate, enrich in pred_enrichments:
    enrich_str = f"{enrich:.2f}x" if enrich != float('inf') else "inf"
    print(f"{role:<20} {count:>8} {link_rate*100:>7.1f}% {base_rate*100:>7.1f}% {enrich_str:>8}")

print(f"\n--- SUCCESSORS (what comes after LINK) ---")
total_successors = sum(successor_roles.values())
total_baseline_succ = sum(baseline_successor.values())

succ_enrichments = []
for role in sorted(set(successor_roles.keys()) | set(baseline_successor.keys())):
    link_rate = successor_roles.get(role, 0) / total_successors if total_successors > 0 else 0
    base_rate = baseline_successor.get(role, 0) / total_baseline_succ if total_baseline_succ > 0 else 0
    enrichment = link_rate / base_rate if base_rate > 0 else float('inf')
    succ_enrichments.append((role, successor_roles.get(role, 0), link_rate, base_rate, enrichment))

succ_enrichments.sort(key=lambda x: -x[4] if x[4] != float('inf') else -999)
print(f"{'Role':<20} {'Count':>8} {'LINK%':>8} {'Base%':>8} {'Enrich':>8}")
print(f"{'-'*20} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")
for role, count, link_rate, base_rate, enrich in succ_enrichments:
    enrich_str = f"{enrich:.2f}x" if enrich != float('inf') else "inf"
    print(f"{role:<20} {count:>8} {link_rate*100:>7.1f}% {base_rate*100:>7.1f}% {enrich_str:>8}")

# Statistical test: chi-square for predecessor/successor distribution vs baseline
print(f"\n{'='*60}")
print(f"STATISTICAL TESTS")
print(f"{'='*60}")

# Build contingency for predecessors
roles_all = sorted(set(predecessor_roles.keys()) | set(baseline_predecessor.keys()))
obs_pred = [predecessor_roles.get(r, 0) for r in roles_all]
exp_pred = [baseline_predecessor.get(r, 0) * total_predecessors / total_baseline_pred for r in roles_all]
# Filter out zeros to avoid division issues
valid_idx = [i for i, (o, e) in enumerate(zip(obs_pred, exp_pred)) if e > 0]
obs_filt = [obs_pred[i] for i in valid_idx]
exp_filt = [exp_pred[i] for i in valid_idx]
if len(obs_filt) > 1:
    chi2_pred, p_pred = stats.chisquare(obs_filt, exp_filt)
else:
    chi2_pred, p_pred = 0, 1.0
print(f"Predecessor distribution vs baseline: chi2={chi2_pred:.1f}, p={p_pred:.2e}")

roles_all_succ = sorted(set(successor_roles.keys()) | set(baseline_successor.keys()))
obs_succ = [successor_roles.get(r, 0) for r in roles_all_succ]
exp_succ = [baseline_successor.get(r, 0) * total_successors / total_baseline_succ for r in roles_all_succ]
valid_idx = [i for i, (o, e) in enumerate(zip(obs_succ, exp_succ)) if e > 0]
obs_filt = [obs_succ[i] for i in valid_idx]
exp_filt = [exp_succ[i] for i in valid_idx]
if len(obs_filt) > 1:
    chi2_succ, p_succ = stats.chisquare(obs_filt, exp_filt)
else:
    chi2_succ, p_succ = 0, 1.0
print(f"Successor distribution vs baseline: chi2={chi2_succ:.1f}, p={p_succ:.2e}")

# Check what role LINK tokens themselves belong to
print(f"\n{'='*60}")
print(f"LINK TOKEN ROLE DISTRIBUTION")
print(f"{'='*60}")
link_roles = Counter()
for t in b_tokens:
    word = t.word.replace('*', '')
    if is_link(word):
        role = token_to_role.get(word, 'HT')
        link_roles[role] += 1

print(f"What roles are LINK tokens themselves?")
for role, count in sorted(link_roles.items(), key=lambda x: -x[1]):
    print(f"  {role}: {count} ({100*count/link_count:.1f}%)")

# C366 verification summary
print(f"\n{'='*60}")
print(f"C366 VERIFICATION")
print(f"{'='*60}")
print(f"\nC366 claims LINK is preceded by AUXILIARY (1.50x), FLOW_OPERATOR (1.30x)")
print(f"C366 claims LINK is followed by HIGH_IMPACT (2.70x), ENERGY_OPERATOR (1.15x)")

# Map legacy role names to current 5-role system
# Legacy AUXILIARY -> AX (Auxiliary)
# Legacy FLOW_OPERATOR -> FL (Flow)
# Legacy HIGH_IMPACT -> ? (possibly CC or EN)
# Legacy ENERGY_OPERATOR -> EN (Energy)

print(f"\nUsing current 5-role taxonomy (AX, EN, FL, FQ, CC, HT):")
print(f"\nPredecessor enrichments:")
for role, count, link_rate, base_rate, enrich in pred_enrichments:
    if role in ['AUXILIARY', 'AX', 'FLOW_OPERATOR', 'FL']:
        print(f"  {role}: {enrich:.2f}x")

print(f"\nSuccessor enrichments:")
for role, count, link_rate, base_rate, enrich in succ_enrichments:
    if role in ['ENERGY_OPERATOR', 'EN', 'HIGH_IMPACT', 'CC', 'CORE_CONTROL']:
        print(f"  {role}: {enrich:.2f}x")

# Summary
print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}")
print(f"LINK tokens show {'SIGNIFICANT' if p_pred < 0.001 else 'NO'} predecessor bias (p={p_pred:.2e})")
print(f"LINK tokens show {'SIGNIFICANT' if p_succ < 0.001 else 'NO'} successor bias (p={p_succ:.2e})")
