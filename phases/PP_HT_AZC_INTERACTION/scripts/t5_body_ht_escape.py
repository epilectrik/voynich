"""
T5: Body HT vs Line-1 HT in Escape Correlation

Quick test to confirm that:
- Body HT (lines 2+) drives the escape correlation
- Line-1 HT is independent of escape rate
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# Load classified token set
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm = json.load(f)
classified_tokens = set(ctm['token_to_class'].keys())

FL_CLASSES = {7, 30, 38, 40}

print("=" * 70)
print("T5: BODY HT vs LINE-1 HT IN ESCAPE CORRELATION")
print("=" * 70)

# Collect data
b_data = defaultdict(lambda: {
    'line1_total': 0, 'line1_ht': 0,
    'body_total': 0, 'body_ht': 0,
    'classified': 0, 'fl': 0,
})

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    folio = token.folio
    line = str(token.line)
    is_ht = w not in classified_tokens

    if line == '1':
        b_data[folio]['line1_total'] += 1
        if is_ht:
            b_data[folio]['line1_ht'] += 1
    else:
        b_data[folio]['body_total'] += 1
        if is_ht:
            b_data[folio]['body_ht'] += 1

    if not is_ht:
        b_data[folio]['classified'] += 1
        cls = int(ctm['token_to_class'][w])
        if cls in FL_CLASSES:
            b_data[folio]['fl'] += 1

# Compute metrics
results = []
for folio in sorted(b_data.keys()):
    d = b_data[folio]
    if d['line1_total'] == 0 or d['body_total'] == 0 or d['classified'] == 0:
        continue

    results.append({
        'folio': folio,
        'line1_ht_pct': 100 * d['line1_ht'] / d['line1_total'],
        'body_ht_pct': 100 * d['body_ht'] / d['body_total'],
        'fl_pct': 100 * d['fl'] / d['classified'],
    })

line1_ht = np.array([r['line1_ht_pct'] for r in results])
body_ht = np.array([r['body_ht_pct'] for r in results])
fl_pcts = np.array([r['fl_pct'] for r in results])

print(f"\nFolios analyzed: {len(results)}")
print(f"\nMean line-1 HT: {np.mean(line1_ht):.1f}%")
print(f"Mean body HT: {np.mean(body_ht):.1f}%")
print(f"Mean FL rate: {np.mean(fl_pcts):.1f}%")

# Correlations
rho_line1, p_line1 = stats.spearmanr(line1_ht, fl_pcts)
rho_body, p_body = stats.spearmanr(body_ht, fl_pcts)

print("\n" + "=" * 70)
print("CORRELATIONS WITH ESCAPE RATE (FL%)")
print("=" * 70)

print(f"\nLine-1 HT vs FL%: rho = {rho_line1:.3f}, p = {p_line1:.4f}")
print(f"Body HT vs FL%: rho = {rho_body:.3f}, p = {p_body:.4f}")

# Compare correlation strengths
z_line1 = np.arctanh(rho_line1)
z_body = np.arctanh(rho_body)
se = np.sqrt(2 / (len(results) - 3))
z_diff = (z_body - z_line1) / se
p_diff = 2 * (1 - stats.norm.cdf(abs(z_diff)))

print(f"\nCorrelation difference test: z = {z_diff:.2f}, p = {p_diff:.4f}")

print("\n" + "=" * 70)
print("VERDICT")
print("=" * 70)

if p_body < 0.05 and p_line1 > 0.05:
    print("""
BODY HT drives the escape correlation.
Line-1 HT is INDEPENDENT of escape rate.

This confirms:
- Line-1 HT = header (A-context declaration)
- Body HT = operational intensity signal (escape tracking)
""")
elif p_body < 0.05 and p_line1 < 0.05:
    print(f"""
BOTH line-1 and body HT correlate with escape.
Body: rho={rho_body:.3f}
Line-1: rho={rho_line1:.3f}
""")
else:
    print(f"""
Neither shows significant correlation.
Body: rho={rho_body:.3f}, p={p_body:.4f}
Line-1: rho={rho_line1:.3f}, p={p_line1:.4f}
""")
