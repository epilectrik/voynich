#!/usr/bin/env python
"""Test if zero both-pass bifolios is significant."""
from scipy.stats import binom

# If pass rate is 25% and r/v are independent
# P(both pass) = 0.25 * 0.25 = 0.0625
# With 24 bifolios, expected both-pass = 1.5

p_both = 0.25 * 0.25
n_bifolios = 24
observed_both = 0

# P(X = 0) where X ~ Binomial(24, 0.0625)
p_zero = binom.pmf(0, n_bifolios, p_both)
print(f'P(both sides pass) = {p_both}')
print(f'Expected both-pass bifolios = {n_bifolios * p_both:.1f}')
print(f'Observed = {observed_both}')
print(f'P(zero both-pass | independent) = {p_zero:.4f}')
print()
if p_zero < 0.05:
    print('SIGNIFICANT: Bifolio sides are NOT independent')
else:
    print('Not significant: Could be chance')
