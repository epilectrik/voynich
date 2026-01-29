"""
T3: Does B-native vocabulary specifically enable escape?

If AZC constrains by limiting vocabulary, and larger vocabularies escape more,
then B-NATIVE vocabulary (not in AZC) should be specifically associated with escape.

Test: Do B-native MIDDLEs have higher escape affinity than AZC-mediated MIDDLEs?
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

print("="*70)
print("T3: DO B-NATIVE MIDDLES SPECIFICALLY ENABLE ESCAPE?")
print("="*70)

# Collect AZC vocabulary
azc_middles = set()
for token in tx.azc():
    m = morph.extract(token.word)
    if m.middle:
        azc_middles.add(m.middle)

print(f"\nAZC unique MIDDLEs: {len(azc_middles)}")

# Collect B tokens and classify by AZC-mediated vs B-native
b_tokens = []
for token in tx.currier_b():
    m = morph.extract(token.word)
    if m.middle:
        is_azc = m.middle in azc_middles
        has_escape = m.suffix and 'e' in m.suffix
        has_kernel = any(c in m.middle for c in ['k', 'h', 'e'])

        b_tokens.append({
            'folio': token.folio,
            'middle': m.middle,
            'is_azc_mediated': is_azc,
            'has_escape_suffix': has_escape,
            'has_kernel_contact': has_kernel
        })

df = pd.DataFrame(b_tokens)
print(f"B tokens with MIDDLE: {len(df)}")

# Compare escape rates between AZC-mediated and B-native
print("\n" + "="*70)
print("ESCAPE RATE BY VOCABULARY SOURCE")
print("="*70)

azc_med = df[df['is_azc_mediated'] == True]
b_native = df[df['is_azc_mediated'] == False]

azc_escape_rate = 100 * azc_med['has_escape_suffix'].mean()
b_native_escape_rate = 100 * b_native['has_escape_suffix'].mean()

print(f"\nAZC-mediated tokens: {len(azc_med)}")
print(f"  Escape rate: {azc_escape_rate:.1f}%")

print(f"\nB-native tokens: {len(b_native)}")
print(f"  Escape rate: {b_native_escape_rate:.1f}%")

# Statistical test
contingency = pd.crosstab(df['is_azc_mediated'], df['has_escape_suffix'])
chi2, p, dof, expected = stats.chi2_contingency(contingency)
print(f"\nChi-squared test: chi2 = {chi2:.1f}, p = {p:.4e}")

if p < 0.05:
    if b_native_escape_rate > azc_escape_rate:
        print("FINDING: B-native vocabulary has HIGHER escape rate ***")
    else:
        print("FINDING: AZC-mediated vocabulary has HIGHER escape rate ***")
else:
    print("FINDING: No significant difference in escape rates")

# Same for kernel contact
print("\n" + "="*70)
print("KERNEL CONTACT BY VOCABULARY SOURCE")
print("="*70)

azc_kernel_rate = 100 * azc_med['has_kernel_contact'].mean()
b_native_kernel_rate = 100 * b_native['has_kernel_contact'].mean()

print(f"\nAZC-mediated kernel contact: {azc_kernel_rate:.1f}%")
print(f"B-native kernel contact: {b_native_kernel_rate:.1f}%")

contingency2 = pd.crosstab(df['is_azc_mediated'], df['has_kernel_contact'])
chi2_k, p_k, _, _ = stats.chi2_contingency(contingency2)
print(f"\nChi-squared test: chi2 = {chi2_k:.1f}, p = {p_k:.4e}")

# Look at specific B-native MIDDLEs with high escape
print("\n" + "="*70)
print("B-NATIVE MIDDLES WITH HIGH ESCAPE AFFINITY")
print("="*70)

# For each B-native MIDDLE, calculate escape rate
b_native_middle_stats = df[df['is_azc_mediated'] == False].groupby('middle').agg({
    'has_escape_suffix': ['sum', 'count', 'mean']
}).reset_index()
b_native_middle_stats.columns = ['middle', 'escape_count', 'total', 'escape_rate']
b_native_middle_stats = b_native_middle_stats[b_native_middle_stats['total'] >= 5]  # min 5 occurrences
b_native_middle_stats = b_native_middle_stats.sort_values('escape_rate', ascending=False)

print(f"\nB-native MIDDLEs with highest escape rates (n>=5):")
for _, row in b_native_middle_stats.head(15).iterrows():
    print(f"  {row['middle']:<15} {row['escape_rate']*100:.0f}% escape ({row['escape_count']:.0f}/{row['total']:.0f})")

print(f"\nB-native MIDDLEs with lowest escape rates (n>=5):")
for _, row in b_native_middle_stats.tail(10).iterrows():
    print(f"  {row['middle']:<15} {row['escape_rate']*100:.0f}% escape ({row['escape_count']:.0f}/{row['total']:.0f})")

# Summary
print("\n" + "="*70)
print("SUMMARY: THE CONSTRAINT MECHANISM")
print("="*70)

if b_native_escape_rate > azc_escape_rate and p < 0.05:
    print("""
CONCRETE MECHANISM IDENTIFIED:

1. AZC vocabulary has LOWER escape capability than B-native vocabulary
2. B folios with more AZC-mediated vocabulary have smaller total vocabulary
3. Smaller vocabulary = fewer B-native options = less escape

Therefore: AZC constrains B by FILTERING OUT high-escape vocabulary.

The A->AZC->B pipeline acts as a VOCABULARY BOTTLENECK that:
- Passes through stable (low-escape) vocabulary
- Blocks or reduces access to volatile (high-escape) vocabulary
- Results in B folios with high AZC-mediation being more constrained

This is NOT about AZC "telling B what to do" - it's about AZC
LIMITING B's options by restricting vocabulary breadth.
""")
    verdict = "BOTTLENECK_CONFIRMED"
else:
    print("""
The escape rates do not differ significantly between AZC-mediated
and B-native vocabulary. The constraint mechanism remains unclear.
""")
    verdict = "MECHANISM_UNCLEAR"

# Save results
output = {
    'azc_mediated_tokens': len(azc_med),
    'b_native_tokens': len(b_native),
    'azc_escape_rate': round(azc_escape_rate, 1),
    'b_native_escape_rate': round(b_native_escape_rate, 1),
    'escape_chi2': round(chi2, 1),
    'escape_p': float(f"{p:.4e}"),
    'azc_kernel_rate': round(azc_kernel_rate, 1),
    'b_native_kernel_rate': round(b_native_kernel_rate, 1),
    'verdict': verdict
}

output_path = PROJECT_ROOT / 'phases' / 'AZC_B_CONSTRAINT_MECHANISM' / 'results' / 't3_b_native_escape.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to: {output_path}")
