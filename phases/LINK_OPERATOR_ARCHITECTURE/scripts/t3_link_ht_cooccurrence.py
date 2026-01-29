"""
T3: LINK-HT Co-occurrence Analysis

T1 showed 38.3% of LINK tokens are HT.
T2 showed LINK and HT share boundary enrichment pattern.

Analyze the LINK-HT relationship:
1. What fraction of HT tokens are LINK?
2. What is the LINK rate among classified (non-HT) tokens?
3. Is the LINK-HT overlap more than expected by chance?
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

def is_ht(word, role_map):
    """HT = not in 49-class grammar"""
    word = word.replace('*', '')
    return role_map.get(word, 'HT') == 'HT'

# Load transcript
tx = Transcript()
b_tokens = list(tx.currier_b())

# Count overlaps
total = 0
link_only = 0
ht_only = 0
both = 0
neither = 0

# Also by position
first_both = 0
first_link = 0
first_ht = 0
first_total = 0
middle_both = 0
middle_link = 0
middle_ht = 0
middle_total = 0
last_both = 0
last_link = 0
last_ht = 0
last_total = 0

lines = defaultdict(list)
for t in b_tokens:
    key = (t.folio, t.line)
    lines[key].append(t)

for key, tokens in lines.items():
    n = len(tokens)
    for i, t in enumerate(tokens):
        word = t.word.replace('*', '')
        if not word.strip():
            continue

        total += 1
        is_l = is_link(word)
        is_h = is_ht(word, token_to_role)

        if is_l and is_h:
            both += 1
        elif is_l and not is_h:
            link_only += 1
        elif not is_l and is_h:
            ht_only += 1
        else:
            neither += 1

        # Position tracking
        if n >= 2:
            if i == 0:
                first_total += 1
                if is_l:
                    first_link += 1
                if is_h:
                    first_ht += 1
                if is_l and is_h:
                    first_both += 1
            elif i == n - 1:
                last_total += 1
                if is_l:
                    last_link += 1
                if is_h:
                    last_ht += 1
                if is_l and is_h:
                    last_both += 1
            else:
                middle_total += 1
                if is_l:
                    middle_link += 1
                if is_h:
                    middle_ht += 1
                if is_l and is_h:
                    middle_both += 1

print(f"{'='*60}")
print(f"LINK-HT OVERLAP ANALYSIS")
print(f"{'='*60}")
print(f"Total tokens: {total}")

print(f"\n--- CONTINGENCY TABLE ---")
print(f"{'':>15} {'HT':>10} {'Non-HT':>10} {'Total':>10}")
print(f"{'LINK':<15} {both:>10} {link_only:>10} {both+link_only:>10}")
print(f"{'Non-LINK':<15} {ht_only:>10} {neither:>10} {ht_only+neither:>10}")
print(f"{'Total':<15} {both+ht_only:>10} {link_only+neither:>10} {total:>10}")

# Rates
total_link = both + link_only
total_ht = both + ht_only
total_classified = link_only + neither

print(f"\n--- RATES ---")
print(f"LINK tokens: {total_link} ({100*total_link/total:.1f}%)")
print(f"HT tokens: {total_ht} ({100*total_ht/total:.1f}%)")
print(f"Both LINK+HT: {both} ({100*both/total:.1f}%)")

print(f"\n% of LINK that are HT: {100*both/total_link:.1f}%")
print(f"% of HT that are LINK: {100*both/total_ht:.1f}%")
print(f"LINK rate among HT: {100*both/total_ht:.1f}%")
print(f"LINK rate among classified (non-HT): {100*link_only/total_classified:.1f}%")

# Fisher's exact test for association
contingency = [[both, link_only], [ht_only, neither]]
odds_ratio, p_fisher = stats.fisher_exact(contingency)
print(f"\n--- STATISTICAL TEST ---")
print(f"Fisher's exact: OR={odds_ratio:.2f}, p={p_fisher:.2e}")

# Chi-square
chi2, p_chi2, dof, expected = stats.chi2_contingency(contingency)
print(f"Chi-square: chi2={chi2:.1f}, p={p_chi2:.2e}")

# Expected overlap under independence
expected_both = (total_link * total_ht) / total
print(f"\nExpected LINK+HT under independence: {expected_both:.0f}")
print(f"Observed LINK+HT: {both}")
print(f"Ratio: {both/expected_both:.2f}x")

# Position-specific analysis
print(f"\n{'='*60}")
print(f"POSITION-SPECIFIC LINK-HT OVERLAP")
print(f"{'='*60}")

def report_position(name, p_both, p_link, p_ht, p_total):
    if p_total == 0:
        return
    exp_both = (p_link * p_ht) / p_total if p_total > 0 else 0
    ratio = p_both / exp_both if exp_both > 0 else 0
    print(f"\n{name}:")
    print(f"  LINK: {p_link}/{p_total} = {100*p_link/p_total:.1f}%")
    print(f"  HT: {p_ht}/{p_total} = {100*p_ht/p_total:.1f}%")
    print(f"  Both: {p_both} (expected: {exp_both:.0f}, ratio: {ratio:.2f}x)")

report_position("First tokens", first_both, first_link, first_ht, first_total)
report_position("Middle tokens", middle_both, middle_link, middle_ht, middle_total)
report_position("Last tokens", last_both, last_link, last_ht, last_total)

# Mechanism analysis
print(f"\n{'='*60}")
print(f"MECHANISM ANALYSIS")
print(f"{'='*60}")

# What words are LINK+HT?
link_ht_words = Counter()
for t in b_tokens:
    word = t.word.replace('*', '')
    if is_link(word) and is_ht(word, token_to_role):
        link_ht_words[word] += 1

print(f"\nTop 20 LINK+HT tokens:")
for word, count in link_ht_words.most_common(20):
    print(f"  {word}: {count}")

# Is the overlap driven by 'ol' being a primitive?
print(f"\n--- OL POSITION IN LINK+HT TOKENS ---")
ol_position = Counter()
for word, count in link_ht_words.items():
    idx = word.find('ol')
    if idx == 0:
        pos = 'START'
    elif idx == len(word) - 2:
        pos = 'END'
    else:
        pos = 'MIDDLE'
    ol_position[pos] += count

print(f"Position of 'ol' in LINK+HT tokens:")
for pos, count in ol_position.most_common():
    print(f"  {pos}: {count} ({100*count/both:.1f}%)")

# Summary
print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}")
if odds_ratio > 1 and p_fisher < 0.001:
    print(f"LINK and HT are POSITIVELY associated (OR={odds_ratio:.2f}, p<0.001)")
    print(f"LINK+HT tokens are {both/expected_both:.2f}x more common than expected")
elif odds_ratio < 1 and p_fisher < 0.001:
    print(f"LINK and HT are NEGATIVELY associated (OR={odds_ratio:.2f}, p<0.001)")
else:
    print(f"LINK and HT are NOT significantly associated (p={p_fisher:.4f})")

print(f"\nInterpretation:")
print(f"  HT tokens contain 'ol' at rate: {100*both/total_ht:.1f}%")
print(f"  Classified tokens contain 'ol' at rate: {100*link_only/total_classified:.1f}%")
if both/total_ht > link_only/total_classified * 1.5:
    print(f"  => HT tokens are {(both/total_ht)/(link_only/total_classified):.2f}x more likely to contain 'ol'")
    print(f"  => 'ol' (LINK marker) is concentrated in the HT vocabulary")
