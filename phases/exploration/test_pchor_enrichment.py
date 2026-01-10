#!/usr/bin/env python
"""Test if pchor first-position enrichment is significant."""
from scipy.stats import binom

# pchor: 4 total occurrences, 2 in first position
# First position: 48 slots out of 4026 total tokens

p_first = 48/4026  # probability of being in first position
observed_first = 2
total_occurrences = 4

# Binomial test: P(X >= 2) where X ~ Binomial(4, 48/4026)
prob_2_or_more = 1 - binom.cdf(1, total_occurrences, p_first)

print(f'=== pchor First-Position Enrichment Test ===')
print()
print(f'Background rate (first position): {p_first:.4f} ({p_first*100:.2f}%)')
print(f'Observed: {observed_first}/{total_occurrences} = {100*observed_first/total_occurrences:.1f}%')
print(f'Enrichment: {(observed_first/total_occurrences) / p_first:.1f}x')
print()
print(f'P(2+ first-position out of 4 if random): {prob_2_or_more:.6f}')
print()

if prob_2_or_more < 0.05:
    print('=> SIGNIFICANT (p < 0.05): pchor is enriched in first position')
elif prob_2_or_more < 0.10:
    print('=> MARGINAL (p < 0.10): pchor shows trend toward first position')
else:
    print('=> NOT SIGNIFICANT: could be random chance')
