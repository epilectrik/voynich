"""
GALLOWS_B_COMPATIBILITY Phase - Test 3
Question: How many B TOKENS are legal per A record?

From AZC-ACT:
  "~80% of B vocabulary filtered per A context (~96 of 480 tokens legal)"
  "Only tokens with MIDDLEs present in the A record are legal for B execution"

This tests the actual filtering magnitude at the token level.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict
import numpy as np

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("TOKEN-LEVEL B FILTERING ANALYSIS")
print("=" * 70)

# Step 1: Build B token vocabulary with MIDDLEs
print("\nStep 1: Building B token -> MIDDLE mapping...")

b_tokens = set()  # Unique B tokens
b_token_to_middle = {}  # token -> MIDDLE
b_middle_to_tokens = defaultdict(set)  # MIDDLE -> set of tokens

for token in tx.currier_b():
    word = token.word
    m = morph.extract(word)
    if m.middle:
        b_tokens.add(word)
        b_token_to_middle[word] = m.middle
        b_middle_to_tokens[m.middle].add(word)

print(f"  Unique B tokens: {len(b_tokens)}")
print(f"  Unique B MIDDLEs: {len(b_middle_to_tokens)}")
print(f"  Mean tokens per MIDDLE: {np.mean([len(v) for v in b_middle_to_tokens.values()]):.2f}")

# Step 2: Build A record -> PP MIDDLEs
print("\nStep 2: Building A record PP profiles...")

a_records = defaultdict(list)
for token in tx.currier_a():
    key = (token.folio, token.line)
    a_records[key].append(token)

# For each A record, extract PP MIDDLEs (those that appear in B)
b_middles = set(b_middle_to_tokens.keys())
record_pp_middles = {}

for (folio, line), tokens in a_records.items():
    middles = set()
    for t in tokens:
        m = morph.extract(t.word)
        if m.middle:
            middles.add(m.middle)
    pp_middles = middles & b_middles
    record_pp_middles[(folio, line)] = pp_middles

print(f"  A records: {len(a_records)}")

# Step 3: For each A record, count legal B tokens
print("\nStep 3: Computing legal B tokens per A record...")

record_legal_tokens = []
for key, pp_middles in record_pp_middles.items():
    legal_tokens = set()
    for mid in pp_middles:
        legal_tokens.update(b_middle_to_tokens[mid])
    record_legal_tokens.append(len(legal_tokens))

legal_arr = np.array(record_legal_tokens)
total_b = len(b_tokens)

print(f"\n  Total B tokens: {total_b}")
print(f"  Mean legal tokens per A record: {np.mean(legal_arr):.1f} ({100*np.mean(legal_arr)/total_b:.1f}%)")
print(f"  Median: {np.median(legal_arr):.1f}")
print(f"  Min: {np.min(legal_arr)}")
print(f"  Max: {np.max(legal_arr)}")
print(f"  Std: {np.std(legal_arr):.1f}")

# Step 4: Distribution of legal token counts
print("\n" + "=" * 70)
print("LEGAL TOKEN DISTRIBUTION")
print("=" * 70)

# Bins as percentage of total B vocabulary
bins_pct = [(0, 5), (5, 10), (10, 20), (20, 30), (30, 50), (50, 100)]
print("\n  Legal tokens as % of B vocabulary:")
for lo_pct, hi_pct in bins_pct:
    lo = total_b * lo_pct / 100
    hi = total_b * hi_pct / 100
    count = sum(1 for t in legal_arr if lo <= t < hi)
    pct = 100 * count / len(legal_arr)
    print(f"    {lo_pct:2d}-{hi_pct:2d}%: {count:4d} records ({pct:5.1f}%)")

# Step 5: "Crippled" analysis - records with very few legal tokens
print("\n" + "=" * 70)
print("CRIPPLING ANALYSIS (token level)")
print("=" * 70)

thresholds_pct = [1, 5, 10, 20]
print("\nRecords below legal token thresholds:")
for thresh_pct in thresholds_pct:
    thresh = total_b * thresh_pct / 100
    count = sum(1 for t in legal_arr if t <= thresh)
    pct = 100 * count / len(legal_arr)
    print(f"  <= {thresh_pct}% ({thresh:.0f} tokens): {count:4d} records ({pct:5.1f}%)")

# Zero legal tokens
zero_count = sum(1 for t in legal_arr if t == 0)
zero_pct = 100 * zero_count / len(legal_arr)
print(f"\n  ZERO legal tokens: {zero_count} records ({zero_pct:.1f}%)")

# Step 6: Verify the "96 of 480" claim from AZC-ACT
print("\n" + "=" * 70)
print("VERIFICATION OF AZC-ACT CLAIM")
print("=" * 70)

# The claim: "~80% of B vocabulary filtered (~96 of 480 tokens legal)"
# This implies ~20% survives
survival_rates = [t / total_b for t in legal_arr]
mean_survival = np.mean(survival_rates)
median_survival = np.median(survival_rates)

print(f"""
AZC-ACT states: "~80% filtered, ~96 of 480 legal" (20% survival)

Observed:
  Mean survival rate: {100*mean_survival:.1f}%
  Median survival rate: {100*median_survival:.1f}%
  Mean legal tokens: {np.mean(legal_arr):.1f} / {total_b}
  Expected (20%): {total_b * 0.2:.1f} tokens
""")

if abs(mean_survival - 0.20) < 0.05:
    print("  -> MATCHES AZC-ACT claim (within 5 percentage points)")
else:
    print(f"  -> DIFFERS from AZC-ACT claim by {100*abs(mean_survival - 0.20):.1f} percentage points")

# Step 7: Gallows domain effect on legal tokens
print("\n" + "=" * 70)
print("GALLOWS DOMAIN EFFECT ON LEGAL TOKENS")
print("=" * 70)

GALLOWS = {'k', 't', 'p', 'f'}

def get_dominant_gallows(middles):
    counts = defaultdict(int)
    for m in middles:
        for g in m:
            if g in GALLOWS:
                counts[g] += 1
    if not counts:
        return None
    return max(counts.keys(), key=lambda g: counts[g])

# Classify A records by gallows domain
record_gallows = {}
for (folio, line), tokens in a_records.items():
    middles = []
    for t in tokens:
        m = morph.extract(t.word)
        if m.middle:
            middles.append(m.middle)
    record_gallows[(folio, line)] = get_dominant_gallows(middles)

# Legal tokens by gallows domain
gallows_legal = defaultdict(list)
for i, ((folio, line), pp_middles) in enumerate(record_pp_middles.items()):
    dom = record_gallows.get((folio, line))
    if dom:
        gallows_legal[dom].append(record_legal_tokens[i])

print("\nMean legal B tokens by A record gallows domain:")
for g in ['k', 't', 'p', 'f']:
    if gallows_legal[g]:
        arr = gallows_legal[g]
        mean_tokens = np.mean(arr)
        pct = 100 * mean_tokens / total_b
        print(f"  {g}-dominant: {mean_tokens:.1f} tokens ({pct:.1f}%), n={len(arr)}")

# Step 8: Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

filtered_pct = 100 * (1 - mean_survival)
crippled_count = sum(1 for t in legal_arr if t / total_b <= 0.10)
crippled_pct = 100 * crippled_count / len(legal_arr)

print(f"""
TOKEN-LEVEL FILTERING:
  - Mean B tokens legal per A record: {np.mean(legal_arr):.1f} ({100*mean_survival:.1f}%)
  - Mean B tokens FILTERED: {filtered_pct:.1f}%

CRIPPLING:
  - Records with <=10% B tokens legal: {crippled_count} ({crippled_pct:.1f}%)
  - Records with ZERO legal tokens: {zero_count} ({zero_pct:.1f}%)

INTERPRETATION:
""")

if mean_survival < 0.30:
    print(f"""  The AZC-ACT claim is approximately correct: ~{filtered_pct:.0f}% of B
  vocabulary is filtered per A context.

  This means A records DO create meaningful B restrictions -
  not by excluding entire folios, but by limiting which TOKENS
  within each folio are legal for execution.

  An A record doesn't say "you can't use program X."
  It says "you can use program X, but only these {np.mean(legal_arr):.0f} tokens."
""")
else:
    print(f"""  The observed survival rate ({100*mean_survival:.1f}%) is higher than
  the AZC-ACT claim (20%). The filtering is less severe than stated.
""")
