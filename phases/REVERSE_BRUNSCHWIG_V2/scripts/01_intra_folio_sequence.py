"""
Test 1: Intra-Folio Sequence Validation

Question: Does the early→mid→late MIDDLE sequence hold within individual folios?

From F-BRU-011:
- EARLY (0.31-0.41): ksh, lch, tch, pch, te (preparation)
- MID (0.42-0.46): k, t, e (thermodynamic core)
- LATE (0.47-0.49): ke, kch (extended operations)

Method:
1. For each folio, compute mean position of each tier's tokens
2. Test if EARLY < MID < LATE holds per-folio
3. Compute consistency rate and statistical significance
"""
import sys
sys.path.insert(0, 'scripts')
from voynich import Transcript, Morphology
from collections import defaultdict
import json
import re

tx = Transcript()
morph = Morphology()
b_tokens = list(tx.currier_b())

HT_PREFIXES = {'yk', 'op', 'yt', 'sa', 'pc', 'do', 'ta'}

# Define tiers from F-BRU-011
EARLY_MIDDLES = {'ksh', 'lch', 'tch', 'pch', 'te'}
MID_MIDDLES = {'k', 't', 'e'}
LATE_MIDDLES = {'ke', 'kch'}

def safe_int(s):
    try:
        return int(s)
    except:
        match = re.match(r'(\d+)', str(s))
        return int(match.group(1)) if match else 0

# Group by folio
by_folio = defaultdict(list)
for t in b_tokens:
    m = morph.extract(t.word)
    if m.prefix and m.prefix in HT_PREFIXES:
        continue
    by_folio[t.folio].append(t)

# Analyze each folio
results = []
folio_details = []

for folio, tokens in by_folio.items():
    tokens_sorted = sorted(tokens, key=lambda t: (safe_int(t.line), 0))
    n_tokens = len(tokens_sorted)
    if n_tokens < 20:
        continue

    early_positions = []
    mid_positions = []
    late_positions = []

    for i, t in enumerate(tokens_sorted):
        m = morph.extract(t.word)
        if not m.middle:
            continue
        pos = i / (n_tokens - 1)

        if m.middle in EARLY_MIDDLES:
            early_positions.append(pos)
        elif m.middle in MID_MIDDLES:
            mid_positions.append(pos)
        elif m.middle in LATE_MIDDLES:
            late_positions.append(pos)

    # Need at least 2 tokens in each tier
    if len(early_positions) >= 2 and len(mid_positions) >= 2 and len(late_positions) >= 2:
        early_mean = sum(early_positions) / len(early_positions)
        mid_mean = sum(mid_positions) / len(mid_positions)
        late_mean = sum(late_positions) / len(late_positions)

        # Check ordering
        early_lt_mid = early_mean < mid_mean
        mid_lt_late = mid_mean < late_mean
        full_order = early_lt_mid and mid_lt_late

        results.append({
            'folio': folio,
            'early_mean': early_mean,
            'mid_mean': mid_mean,
            'late_mean': late_mean,
            'early_n': len(early_positions),
            'mid_n': len(mid_positions),
            'late_n': len(late_positions),
            'early_lt_mid': early_lt_mid,
            'mid_lt_late': mid_lt_late,
            'full_order': full_order,
        })

print("=" * 70)
print("TEST 1: INTRA-FOLIO SEQUENCE VALIDATION")
print("=" * 70)
print()
print("Question: Does EARLY < MID < LATE hold within individual folios?")
print()

# Statistics
n_folios = len(results)
early_lt_mid_count = sum(1 for r in results if r['early_lt_mid'])
mid_lt_late_count = sum(1 for r in results if r['mid_lt_late'])
full_order_count = sum(1 for r in results if r['full_order'])

print(f"Folios with sufficient data (>=2 tokens per tier): {n_folios}")
print()
print("ORDERING RESULTS:")
print("-" * 50)
print(f"  EARLY < MID:  {early_lt_mid_count}/{n_folios} = {early_lt_mid_count/n_folios*100:.1f}%")
print(f"  MID < LATE:   {mid_lt_late_count}/{n_folios} = {mid_lt_late_count/n_folios*100:.1f}%")
print(f"  FULL ORDER:   {full_order_count}/{n_folios} = {full_order_count/n_folios*100:.1f}%")
print()

# Binomial test
from scipy import stats
# Expected by chance: each ordering has 50% probability
# Full order by chance: 25%
p_full = stats.binomtest(full_order_count, n_folios, 0.25, alternative='greater').pvalue
p_early_mid = stats.binomtest(early_lt_mid_count, n_folios, 0.5, alternative='greater').pvalue
p_mid_late = stats.binomtest(mid_lt_late_count, n_folios, 0.5, alternative='greater').pvalue

print("STATISTICAL TESTS (binomial):")
print("-" * 50)
print(f"  EARLY < MID:  p = {p_early_mid:.6f} (vs 50% chance)")
print(f"  MID < LATE:   p = {p_mid_late:.6f} (vs 50% chance)")
print(f"  FULL ORDER:   p = {p_full:.6f} (vs 25% chance)")
print()

# Aggregate statistics
all_early = sum(r['early_mean'] for r in results) / n_folios
all_mid = sum(r['mid_mean'] for r in results) / n_folios
all_late = sum(r['late_mean'] for r in results) / n_folios

print("AGGREGATE MEAN POSITIONS:")
print("-" * 50)
print(f"  EARLY tier (prep):   {all_early:.3f}")
print(f"  MID tier (thermo):   {all_mid:.3f}")
print(f"  LATE tier (extended):{all_late:.3f}")
print()

# Verdict
if full_order_count / n_folios >= 0.6 and p_full < 0.05:
    verdict = "CONFIRMED"
elif full_order_count / n_folios >= 0.5 and p_full < 0.1:
    verdict = "SUPPORT"
elif full_order_count / n_folios >= 0.4:
    verdict = "WEAK"
else:
    verdict = "NOT SUPPORTED"

print("=" * 70)
print(f"VERDICT: {verdict}")
print("=" * 70)

if verdict in ["CONFIRMED", "SUPPORT"]:
    print("\nInterpretation: The three-tier MIDDLE sequence (preparation -> thermodynamic")
    print("-> extended) holds within individual folios, not just in aggregate.")

# Output JSON
output = {
    "test": "Intra-Folio Sequence Validation",
    "question": "Does EARLY < MID < LATE MIDDLE sequence hold within folios?",
    "n_folios": n_folios,
    "results": {
        "early_lt_mid": {
            "count": early_lt_mid_count,
            "rate": early_lt_mid_count / n_folios,
            "p_value": p_early_mid
        },
        "mid_lt_late": {
            "count": mid_lt_late_count,
            "rate": mid_lt_late_count / n_folios,
            "p_value": p_mid_late
        },
        "full_order": {
            "count": full_order_count,
            "rate": full_order_count / n_folios,
            "p_value": p_full
        }
    },
    "aggregate_means": {
        "early": all_early,
        "mid": all_mid,
        "late": all_late
    },
    "verdict": verdict
}

with open('phases/REVERSE_BRUNSCHWIG_V2/results/intra_folio_sequence.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\nOutput saved to phases/REVERSE_BRUNSCHWIG_V2/results/intra_folio_sequence.json")
