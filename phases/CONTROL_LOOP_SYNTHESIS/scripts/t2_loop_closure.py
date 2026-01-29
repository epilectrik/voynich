"""
T2: Loop Closure Analysis

Is the control loop closed? Does FL return to KERNEL?
- What follows FL tokens?
- Is there a FL→KERNEL path?
- What's the return mechanism after escape?
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

def get_kernel_type(word):
    word = word.replace('*', '').lower()
    kernels = []
    if 'k' in word: kernels.append('k')
    if 'h' in word: kernels.append('h')
    if 'e' in word: kernels.append('e')
    return kernels

# Load transcript
tx = Transcript()
b_tokens = list(tx.currier_b())

lines = defaultdict(list)
for t in b_tokens:
    lines[(t.folio, t.line)].append(t)

print(f"Total B tokens: {len(b_tokens)}")

# What follows FL?
post_fl_roles = Counter()
post_fl_link = 0
post_fl_kernel = 0
post_fl_kernel_types = Counter()
post_fl_total = 0

# What follows FL at distance 2?
post_fl_d2_kernel = 0
post_fl_d2_link = 0
post_fl_d2_total = 0

# FL→FL sequences (chained escape)
fl_to_fl = 0

for key, tokens in lines.items():
    for i, t in enumerate(tokens):
        word = t.word.replace('*', '')
        if not word.strip():
            continue

        if is_fl(word):
            # Immediate successor
            if i < len(tokens) - 1:
                next_word = tokens[i+1].word.replace('*', '')
                if next_word.strip():
                    post_fl_total += 1
                    next_role = token_to_role.get(next_word, 'HT')
                    post_fl_roles[next_role] += 1

                    if is_link(next_word):
                        post_fl_link += 1
                    if has_kernel(next_word):
                        post_fl_kernel += 1
                        for k in get_kernel_type(next_word):
                            post_fl_kernel_types[k] += 1
                    if is_fl(next_word):
                        fl_to_fl += 1

            # Distance 2 successor
            if i < len(tokens) - 2:
                d2_word = tokens[i+2].word.replace('*', '')
                if d2_word.strip():
                    post_fl_d2_total += 1
                    if has_kernel(d2_word):
                        post_fl_d2_kernel += 1
                    if is_link(d2_word):
                        post_fl_d2_link += 1

# Baseline rates
total_tokens = len(b_tokens)
fl_rate = sum(1 for t in b_tokens if is_fl(t.word)) / total_tokens
link_rate = sum(1 for t in b_tokens if is_link(t.word)) / total_tokens
kernel_rate = sum(1 for t in b_tokens if has_kernel(t.word)) / total_tokens

print(f"\n{'='*60}")
print(f"LOOP CLOSURE ANALYSIS")
print(f"{'='*60}")

print(f"\nBaseline rates:")
print(f"  FL: {fl_rate*100:.1f}%")
print(f"  LINK: {link_rate*100:.1f}%")
print(f"  Kernel: {kernel_rate*100:.1f}%")

print(f"\n--- WHAT FOLLOWS FL? (distance 1) ---")
print(f"Total FL with successors: {post_fl_total}")
print(f"\nRole distribution:")
for role, count in sorted(post_fl_roles.items(), key=lambda x: -x[1]):
    pct = 100 * count / post_fl_total
    print(f"  {role}: {count} ({pct:.1f}%)")

print(f"\nSpecific markers:")
print(f"  Kernel follows FL: {post_fl_kernel}/{post_fl_total} = {100*post_fl_kernel/post_fl_total:.1f}% (baseline: {kernel_rate*100:.1f}%)")
print(f"  LINK follows FL: {post_fl_link}/{post_fl_total} = {100*post_fl_link/post_fl_total:.1f}% (baseline: {link_rate*100:.1f}%)")
print(f"  FL follows FL: {fl_to_fl}/{post_fl_total} = {100*fl_to_fl/post_fl_total:.1f}% (baseline: {fl_rate*100:.1f}%)")

kernel_enrich = (post_fl_kernel/post_fl_total) / kernel_rate if kernel_rate > 0 else 0
link_enrich = (post_fl_link/post_fl_total) / link_rate if link_rate > 0 else 0
fl_enrich = (fl_to_fl/post_fl_total) / fl_rate if fl_rate > 0 else 0

print(f"\nEnrichment:")
print(f"  Kernel: {kernel_enrich:.2f}x")
print(f"  LINK: {link_enrich:.2f}x")
print(f"  FL: {fl_enrich:.2f}x")

print(f"\n--- KERNEL TYPE AFTER FL ---")
for k, count in sorted(post_fl_kernel_types.items(), key=lambda x: -x[1]):
    print(f"  '{k}' follows FL: {count} ({100*count/post_fl_total:.1f}%)")

print(f"\n--- DISTANCE 2 PATTERNS ---")
if post_fl_d2_total > 0:
    print(f"Kernel at d=2 after FL: {post_fl_d2_kernel}/{post_fl_d2_total} = {100*post_fl_d2_kernel/post_fl_d2_total:.1f}%")
    print(f"LINK at d=2 after FL: {post_fl_d2_link}/{post_fl_d2_total} = {100*post_fl_d2_link/post_fl_d2_total:.1f}%")

# Test if FL chains (FL→FL→...) exist
print(f"\n--- FL CHAINING ---")
print(f"FL->FL direct transitions: {fl_to_fl}")
print(f"FL->FL rate: {100*fl_to_fl/post_fl_total:.1f}% vs baseline {fl_rate*100:.1f}%")
print(f"FL chaining enrichment: {fl_enrich:.2f}x")

# Summary
print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}")

if kernel_enrich > 1.2:
    print(f"FL->KERNEL path EXISTS ({kernel_enrich:.2f}x enrichment)")
    print(f"  Loop is CLOSED: FL returns to kernel processing")
elif kernel_enrich > 0.8:
    print(f"FL->KERNEL at baseline ({kernel_enrich:.2f}x)")
    print(f"  Loop closure is NEUTRAL")
else:
    print(f"FL->KERNEL is DEPLETED ({kernel_enrich:.2f}x)")
    print(f"  FL does NOT directly return to kernel")

if link_enrich > 1.2:
    print(f"FL->LINK path exists ({link_enrich:.2f}x) - return to monitoring")
elif link_enrich < 0.8:
    print(f"FL->LINK is depleted ({link_enrich:.2f}x) - confirms separation")

if fl_enrich > 1.5:
    print(f"FL chains are common ({fl_enrich:.2f}x) - extended escape sequences")
