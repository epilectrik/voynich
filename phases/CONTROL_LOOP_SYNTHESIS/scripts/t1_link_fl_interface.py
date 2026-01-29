"""
T1: LINK-FL Interface Analysis

What triggers the transition from LINK (monitoring) to FL (escape)?
- What tokens immediately precede FL?
- Is there a LINK→FL direct transition?
- What's the "bridge" between monitoring and escape?
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
    return 'ol' in word.replace('*', '')

def is_fl(word):
    return token_to_role.get(word.replace('*', ''), 'HT') == 'FLOW_OPERATOR'

def has_kernel(word):
    word = word.replace('*', '').lower()
    return 'k' in word or 'h' in word or 'e' in word

# Load transcript
tx = Transcript()
b_tokens = list(tx.currier_b())

lines = defaultdict(list)
for t in b_tokens:
    lines[(t.folio, t.line)].append(t)

print(f"Total B tokens: {len(b_tokens)}")
print(f"Total lines: {len(lines)}")

# What immediately precedes FL?
pre_fl_roles = Counter()
pre_fl_link = 0
pre_fl_kernel = 0
pre_fl_total = 0

# What immediately follows LINK?
post_link_roles = Counter()
post_link_fl = 0
post_link_kernel = 0
post_link_total = 0

# Direct LINK→FL transitions
link_to_fl_direct = 0

for key, tokens in lines.items():
    for i, t in enumerate(tokens):
        word = t.word.replace('*', '')
        if not word.strip():
            continue

        # What precedes FL?
        if is_fl(word) and i > 0:
            prev_word = tokens[i-1].word.replace('*', '')
            if prev_word.strip():
                pre_fl_total += 1
                prev_role = token_to_role.get(prev_word, 'HT')
                pre_fl_roles[prev_role] += 1
                if is_link(prev_word):
                    pre_fl_link += 1
                if has_kernel(prev_word):
                    pre_fl_kernel += 1

        # What follows LINK?
        if is_link(word) and i < len(tokens) - 1:
            next_word = tokens[i+1].word.replace('*', '')
            if next_word.strip():
                post_link_total += 1
                next_role = token_to_role.get(next_word, 'HT')
                post_link_roles[next_role] += 1
                if is_fl(next_word):
                    post_link_fl += 1
                    link_to_fl_direct += 1
                if has_kernel(next_word):
                    post_link_kernel += 1

print(f"\n{'='*60}")
print(f"LINK->FL INTERFACE ANALYSIS")
print(f"{'='*60}")

# Baseline rates
total_tokens = len(b_tokens)
fl_rate = sum(1 for t in b_tokens if is_fl(t.word)) / total_tokens
link_rate = sum(1 for t in b_tokens if is_link(t.word)) / total_tokens
kernel_rate = sum(1 for t in b_tokens if has_kernel(t.word)) / total_tokens

print(f"\nBaseline rates:")
print(f"  FL: {fl_rate*100:.1f}%")
print(f"  LINK: {link_rate*100:.1f}%")
print(f"  Kernel (k/h/e): {kernel_rate*100:.1f}%")

print(f"\n--- WHAT PRECEDES FL? ---")
print(f"Total FL tokens with predecessors: {pre_fl_total}")
print(f"\nRole distribution:")
for role, count in sorted(pre_fl_roles.items(), key=lambda x: -x[1]):
    pct = 100 * count / pre_fl_total
    print(f"  {role}: {count} ({pct:.1f}%)")

print(f"\nSpecific markers:")
print(f"  LINK precedes FL: {pre_fl_link}/{pre_fl_total} = {100*pre_fl_link/pre_fl_total:.1f}% (baseline: {link_rate*100:.1f}%)")
print(f"  Kernel precedes FL: {pre_fl_kernel}/{pre_fl_total} = {100*pre_fl_kernel/pre_fl_total:.1f}% (baseline: {kernel_rate*100:.1f}%)")

pre_link_enrich = (pre_fl_link/pre_fl_total) / link_rate if link_rate > 0 else 0
pre_kernel_enrich = (pre_fl_kernel/pre_fl_total) / kernel_rate if kernel_rate > 0 else 0
print(f"  LINK enrichment: {pre_link_enrich:.2f}x")
print(f"  Kernel enrichment: {pre_kernel_enrich:.2f}x")

print(f"\n--- WHAT FOLLOWS LINK? ---")
print(f"Total LINK tokens with successors: {post_link_total}")
print(f"\nRole distribution:")
for role, count in sorted(post_link_roles.items(), key=lambda x: -x[1]):
    pct = 100 * count / post_link_total
    print(f"  {role}: {count} ({pct:.1f}%)")

print(f"\nSpecific markers:")
print(f"  FL follows LINK: {post_link_fl}/{post_link_total} = {100*post_link_fl/post_link_total:.1f}% (baseline: {fl_rate*100:.1f}%)")
print(f"  Kernel follows LINK: {post_link_kernel}/{post_link_total} = {100*post_link_kernel/post_link_total:.1f}% (baseline: {kernel_rate*100:.1f}%)")

post_fl_enrich = (post_link_fl/post_link_total) / fl_rate if fl_rate > 0 else 0
post_kernel_enrich = (post_link_kernel/post_link_total) / kernel_rate if kernel_rate > 0 else 0
print(f"  FL enrichment: {post_fl_enrich:.2f}x")
print(f"  Kernel enrichment: {post_kernel_enrich:.2f}x")

print(f"\n--- DIRECT LINK->FL TRANSITIONS ---")
print(f"Direct LINK->FL: {link_to_fl_direct}")
expected_link_fl = post_link_total * fl_rate
print(f"Expected under independence: {expected_link_fl:.0f}")
print(f"Ratio: {link_to_fl_direct/expected_link_fl:.2f}x")

# Summary
print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}")
if pre_link_enrich < 0.8:
    print(f"LINK is DEPLETED before FL ({pre_link_enrich:.2f}x) - confirms C807")
elif pre_link_enrich > 1.2:
    print(f"LINK is ENRICHED before FL ({pre_link_enrich:.2f}x)")
else:
    print(f"LINK is at BASELINE before FL ({pre_link_enrich:.2f}x)")

if post_fl_enrich < 0.8:
    print(f"FL is DEPLETED after LINK ({post_fl_enrich:.2f}x) - confirms C807")
elif post_fl_enrich > 1.2:
    print(f"FL is ENRICHED after LINK ({post_fl_enrich:.2f}x)")
else:
    print(f"FL is at BASELINE after LINK ({post_fl_enrich:.2f}x)")

if pre_kernel_enrich > 1.2:
    print(f"Kernel is ENRICHED before FL ({pre_kernel_enrich:.2f}x) - FL triggered from kernel states")
