"""
T1: Length-Controlled Baseline Test

Question: Is the 84.8% compound rate for line-1 folio-unique MIDDLEs
significantly above what we'd expect from random strings of the same length?

Method:
1. Get the length distribution of line-1 folio-unique MIDDLEs
2. Generate random strings of same lengths using B's character inventory
3. Check what % of random strings contain core MIDDLEs
4. Compare to observed 84.8%
"""

import json
import sys
import random
from pathlib import Path
from collections import Counter, defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

random.seed(42)

tx = Transcript()
morph = Morphology()

# Load classified token set
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm = json.load(f)
classified_tokens = set(ctm['token_to_class'].keys())

# Build MIDDLE -> folios mapping and get character inventory
middle_to_folios = defaultdict(set)
all_middle_chars = Counter()

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if m.middle:
        middle_to_folios[m.middle].add(token.folio)
        for c in m.middle:
            all_middle_chars[c] += 1

# Character inventory for random generation
char_inventory = list(all_middle_chars.keys())
char_weights = [all_middle_chars[c] for c in char_inventory]

folio_unique_middles = {mid for mid, folios in middle_to_folios.items() if len(folios) == 1}
core_middles = {mid for mid, folios in middle_to_folios.items() if len(folios) >= 20}

print(f"Setup:")
print(f"  Character inventory: {len(char_inventory)} chars")
print(f"  Core MIDDLEs (20+ folios): {len(core_middles)}")
print(f"  Folio-unique MIDDLEs: {len(folio_unique_middles)}")
print()

# Collect line-1 folio-unique MIDDLEs
folio_lines = defaultdict(lambda: defaultdict(list))
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    folio_lines[token.folio][token.line].append({
        'word': w,
        'is_ht': w not in classified_tokens
    })

line1_folio_unique_mids = []
for folio, lines in folio_lines.items():
    sorted_lines = sorted(lines.keys())
    if not sorted_lines:
        continue
    first_line = sorted_lines[0]

    for tok in lines[first_line]:
        if tok['is_ht']:
            m = morph.extract(tok['word'])
            if m.middle and m.middle in folio_unique_middles:
                line1_folio_unique_mids.append(m.middle)

unique_line1_fum = list(set(line1_folio_unique_mids))
print(f"Line-1 folio-unique MIDDLEs: {len(unique_line1_fum)}")

# Get length distribution
lengths = [len(m) for m in unique_line1_fum]
print(f"Length distribution: min={min(lengths)}, max={max(lengths)}, mean={sum(lengths)/len(lengths):.2f}")
print()

def contains_core(middle, core_set, min_len=2):
    """Check if middle contains any core MIDDLE as substring"""
    for core in core_set:
        if len(core) >= min_len and core in middle and core != middle:
            return True
    return False

# Observed rate
observed_compound = sum(1 for m in unique_line1_fum if contains_core(m, core_middles))
observed_rate = 100 * observed_compound / len(unique_line1_fum)
print(f"Observed compound rate: {observed_compound}/{len(unique_line1_fum)} = {observed_rate:.1f}%")

# Generate random strings of same lengths and test
def generate_random_middle(length):
    """Generate random string using B's character inventory (weighted)"""
    return ''.join(random.choices(char_inventory, weights=char_weights, k=length))

n_iterations = 1000
random_rates = []

for i in range(n_iterations):
    random_middles = [generate_random_middle(len(m)) for m in unique_line1_fum]
    random_compound = sum(1 for m in random_middles if contains_core(m, core_middles))
    random_rates.append(100 * random_compound / len(random_middles))

mean_random = sum(random_rates) / len(random_rates)
std_random = (sum((r - mean_random)**2 for r in random_rates) / len(random_rates))**0.5
z_score = (observed_rate - mean_random) / std_random if std_random > 0 else 0

print(f"\nRandom baseline ({n_iterations} iterations):")
print(f"  Mean random compound rate: {mean_random:.1f}%")
print(f"  Std: {std_random:.2f}%")
print(f"  Min: {min(random_rates):.1f}%, Max: {max(random_rates):.1f}%")
print(f"\nComparison:")
print(f"  Observed: {observed_rate:.1f}%")
print(f"  Random baseline: {mean_random:.1f}%")
print(f"  Elevation: +{observed_rate - mean_random:.1f}pp")
print(f"  Z-score: {z_score:.2f}")

# How many random iterations exceeded observed?
n_exceeded = sum(1 for r in random_rates if r >= observed_rate)
p_value = n_exceeded / n_iterations

print(f"  P-value (empirical): {p_value:.4f} ({n_exceeded}/{n_iterations} exceeded)")

# Verdict
print("\n" + "="*60)
print("VERDICT")
print("="*60)

if observed_rate > mean_random + 10 and p_value < 0.01:
    verdict = "SIGNIFICANTLY_ABOVE_CHANCE"
    explanation = f"Compound rate {observed_rate:.1f}% is {observed_rate - mean_random:.1f}pp above random baseline (p={p_value:.4f})"
elif observed_rate > mean_random + 5:
    verdict = "MODERATELY_ABOVE_CHANCE"
    explanation = f"Compound rate elevated but effect size modest (+{observed_rate - mean_random:.1f}pp)"
else:
    verdict = "NOT_ABOVE_CHANCE"
    explanation = f"Compound rate {observed_rate:.1f}% is within random expectation ({mean_random:.1f}%)"

print(f"\n{verdict}: {explanation}")

# Save results
results = {
    'observed': {
        'n_middles': len(unique_line1_fum),
        'compound_count': observed_compound,
        'compound_rate': observed_rate
    },
    'random_baseline': {
        'n_iterations': n_iterations,
        'mean_rate': mean_random,
        'std_rate': std_random,
        'min_rate': min(random_rates),
        'max_rate': max(random_rates)
    },
    'comparison': {
        'elevation_pp': observed_rate - mean_random,
        'z_score': z_score,
        'p_value': p_value
    },
    'verdict': verdict
}

out_path = PROJECT_ROOT / 'phases' / 'COMPOUND_MIDDLE_ARCHITECTURE' / 'results' / 't1_length_baseline.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path}")
