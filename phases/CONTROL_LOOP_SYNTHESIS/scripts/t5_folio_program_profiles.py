"""
T5: Folio Program Profiles

Why do folios differ in escape rates?
- What's the phase composition of high vs low escape folios?
- Do kernel/link/fl ratios predict folio behavior?
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

def is_ht(word):
    return token_to_role.get(word.replace('*', ''), 'HT') == 'HT'

def has_kernel(word):
    word = word.replace('*', '').lower()
    return 'k' in word or 'h' in word or 'e' in word

# Load transcript
tx = Transcript()
b_tokens = list(tx.currier_b())

# Compute per-folio stats
folio_stats = defaultdict(lambda: {
    'total': 0, 'kernel': 0, 'link': 0, 'fl': 0, 'ht': 0,
    'kernel_only': 0, 'link_only': 0  # Exclusive categories
})

for t in b_tokens:
    word = t.word.replace('*', '')
    if not word.strip():
        continue

    f = t.folio
    folio_stats[f]['total'] += 1

    if has_kernel(word):
        folio_stats[f]['kernel'] += 1
    if is_link(word):
        folio_stats[f]['link'] += 1
    if is_fl(word):
        folio_stats[f]['fl'] += 1
    if is_ht(word):
        folio_stats[f]['ht'] += 1

    # Exclusive: kernel but not link
    if has_kernel(word) and not is_link(word):
        folio_stats[f]['kernel_only'] += 1
    # Exclusive: link but not kernel
    if is_link(word) and not has_kernel(word):
        folio_stats[f]['link_only'] += 1

# Calculate rates
folios = sorted(folio_stats.keys())
data = []

for f in folios:
    s = folio_stats[f]
    if s['total'] < 50:  # Skip small folios
        continue

    data.append({
        'folio': f,
        'total': s['total'],
        'kernel_rate': 100 * s['kernel'] / s['total'],
        'link_rate': 100 * s['link'] / s['total'],
        'fl_rate': 100 * s['fl'] / s['total'],
        'ht_rate': 100 * s['ht'] / s['total'],
        'kernel_only_rate': 100 * s['kernel_only'] / s['total'],
        'link_only_rate': 100 * s['link_only'] / s['total'],
    })

print(f"Total folios with 50+ tokens: {len(data)}")

# Convert to arrays for analysis
kernel_rates = np.array([d['kernel_rate'] for d in data])
link_rates = np.array([d['link_rate'] for d in data])
fl_rates = np.array([d['fl_rate'] for d in data])
ht_rates = np.array([d['ht_rate'] for d in data])
kernel_only = np.array([d['kernel_only_rate'] for d in data])
link_only = np.array([d['link_only_rate'] for d in data])

print(f"\n{'='*60}")
print(f"FOLIO PROGRAM PROFILES")
print(f"{'='*60}")

print(f"\n--- RATE DISTRIBUTIONS ---")
print(f"{'Metric':<20} {'Mean':>8} {'Std':>8} {'Min':>8} {'Max':>8}")
print(f"{'-'*20} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")
print(f"{'KERNEL':<20} {np.mean(kernel_rates):>7.1f}% {np.std(kernel_rates):>7.1f}% {np.min(kernel_rates):>7.1f}% {np.max(kernel_rates):>7.1f}%")
print(f"{'LINK':<20} {np.mean(link_rates):>7.1f}% {np.std(link_rates):>7.1f}% {np.min(link_rates):>7.1f}% {np.max(link_rates):>7.1f}%")
print(f"{'FL':<20} {np.mean(fl_rates):>7.1f}% {np.std(fl_rates):>7.1f}% {np.min(fl_rates):>7.1f}% {np.max(fl_rates):>7.1f}%")
print(f"{'HT':<20} {np.mean(ht_rates):>7.1f}% {np.std(ht_rates):>7.1f}% {np.min(ht_rates):>7.1f}% {np.max(ht_rates):>7.1f}%")

print(f"\n--- PHASE CORRELATIONS ---")
# Kernel vs FL
rho, p = stats.spearmanr(kernel_rates, fl_rates)
print(f"KERNEL vs FL: rho={rho:.3f}, p={p:.4f}")

# Link vs FL
rho, p = stats.spearmanr(link_rates, fl_rates)
print(f"LINK vs FL: rho={rho:.3f}, p={p:.4f}")

# Kernel vs Link
rho, p = stats.spearmanr(kernel_rates, link_rates)
print(f"KERNEL vs LINK: rho={rho:.3f}, p={p:.4f}")

# HT vs FL (reference: C796)
rho, p = stats.spearmanr(ht_rates, fl_rates)
print(f"HT vs FL: rho={rho:.3f}, p={p:.4f}")

# Kernel vs HT
rho, p = stats.spearmanr(kernel_rates, ht_rates)
print(f"KERNEL vs HT: rho={rho:.3f}, p={p:.4f}")

# Link vs HT
rho, p = stats.spearmanr(link_rates, ht_rates)
print(f"LINK vs HT: rho={rho:.3f}, p={p:.4f}")

print(f"\n--- EXCLUSIVE CATEGORY CORRELATIONS ---")
# Kernel-only vs FL
rho, p = stats.spearmanr(kernel_only, fl_rates)
print(f"KERNEL-only (no 'ol') vs FL: rho={rho:.3f}, p={p:.4f}")

# Link-only vs FL
rho, p = stats.spearmanr(link_only, fl_rates)
print(f"LINK-only (no k/h/e) vs FL: rho={rho:.3f}, p={p:.4f}")

# Tertile analysis
print(f"\n--- FL TERTILE ANALYSIS ---")
fl_tertiles = np.percentile(fl_rates, [33.3, 66.7])
low_fl = [d for d in data if d['fl_rate'] <= fl_tertiles[0]]
mid_fl = [d for d in data if fl_tertiles[0] < d['fl_rate'] <= fl_tertiles[1]]
high_fl = [d for d in data if d['fl_rate'] > fl_tertiles[1]]

print(f"\nLow FL folios (n={len(low_fl)}, FL<={fl_tertiles[0]:.1f}%):")
print(f"  Mean KERNEL: {np.mean([d['kernel_rate'] for d in low_fl]):.1f}%")
print(f"  Mean LINK: {np.mean([d['link_rate'] for d in low_fl]):.1f}%")
print(f"  Mean HT: {np.mean([d['ht_rate'] for d in low_fl]):.1f}%")

print(f"\nMid FL folios (n={len(mid_fl)}):")
print(f"  Mean KERNEL: {np.mean([d['kernel_rate'] for d in mid_fl]):.1f}%")
print(f"  Mean LINK: {np.mean([d['link_rate'] for d in mid_fl]):.1f}%")
print(f"  Mean HT: {np.mean([d['ht_rate'] for d in mid_fl]):.1f}%")

print(f"\nHigh FL folios (n={len(high_fl)}, FL>{fl_tertiles[1]:.1f}%):")
print(f"  Mean KERNEL: {np.mean([d['kernel_rate'] for d in high_fl]):.1f}%")
print(f"  Mean LINK: {np.mean([d['link_rate'] for d in high_fl]):.1f}%")
print(f"  Mean HT: {np.mean([d['ht_rate'] for d in high_fl]):.1f}%")

# Summary
print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}")

# Check what predicts FL rate
predictors = [
    ('KERNEL', stats.spearmanr(kernel_rates, fl_rates)),
    ('LINK', stats.spearmanr(link_rates, fl_rates)),
    ('HT', stats.spearmanr(ht_rates, fl_rates)),
    ('KERNEL-only', stats.spearmanr(kernel_only, fl_rates)),
    ('LINK-only', stats.spearmanr(link_only, fl_rates)),
]

print(f"Predictors of FL (escape) rate:")
for name, (rho, p) in sorted(predictors, key=lambda x: -abs(x[1][0])):
    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
    print(f"  {name}: rho={rho:.3f} {sig}")
