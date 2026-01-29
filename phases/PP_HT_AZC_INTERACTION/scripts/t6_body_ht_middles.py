"""
T6: Body HT MIDDLE Patterns

Questions:
1. What MIDDLEs appear in body HT?
2. Do they differ from line-1 HT MIDDLEs?
3. Are body HT MIDDLEs PP or B-exclusive?
4. Do high-escape folios use different body HT MIDDLEs?
5. Any positional patterns (early vs late in line)?
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
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
print("T6: BODY HT MIDDLE PATTERNS")
print("=" * 70)

# Collect A vocabulary for PP classification
all_a_middles = set()
for token in tx.currier_a():
    w = token.word.strip()
    if w and '*' not in w:
        m = morph.extract(w)
        if m.middle:
            all_a_middles.add(m.middle)

print(f"\nA unique MIDDLEs (PP pool): {len(all_a_middles)}")

# Collect HT MIDDLEs by location
line1_ht_middles = []
body_ht_middles = []
body_ht_by_folio = defaultdict(list)
body_ht_positions = []  # (normalized_position, middle)

# Also track FL rate per folio
folio_fl = defaultdict(lambda: {'classified': 0, 'fl': 0})

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    folio = token.folio
    line = str(token.line)
    is_ht = w not in classified_tokens
    m = morph.extract(w)

    if not is_ht:
        folio_fl[folio]['classified'] += 1
        cls = int(ctm['token_to_class'][w])
        if cls in FL_CLASSES:
            folio_fl[folio]['fl'] += 1

    if is_ht and m.middle:
        if line == '1':
            line1_ht_middles.append(m.middle)
        else:
            body_ht_middles.append(m.middle)
            body_ht_by_folio[folio].append(m.middle)

            # Track position
            if hasattr(token, 'position') and token.position:
                body_ht_positions.append((token.position, m.middle))

print(f"\nLine-1 HT MIDDLEs: {len(line1_ht_middles)} tokens, {len(set(line1_ht_middles))} types")
print(f"Body HT MIDDLEs: {len(body_ht_middles)} tokens, {len(set(body_ht_middles))} types")

# ============================================================
# TEST 1: Most common body HT MIDDLEs
# ============================================================
print("\n" + "=" * 70)
print("TEST 1: MOST COMMON BODY HT MIDDLES")
print("=" * 70)

body_counter = Counter(body_ht_middles)
line1_counter = Counter(line1_ht_middles)

print(f"\nTop 20 body HT MIDDLEs:")
for mid, count in body_counter.most_common(20):
    is_pp = "PP" if mid in all_a_middles else "B-excl"
    line1_count = line1_counter.get(mid, 0)
    print(f"  '{mid}': {count} ({is_pp}) [line1: {line1_count}]")

# ============================================================
# TEST 2: PP vs B-exclusive in body HT
# ============================================================
print("\n" + "=" * 70)
print("TEST 2: PP vs B-EXCLUSIVE IN BODY HT")
print("=" * 70)

body_pp = [m for m in body_ht_middles if m in all_a_middles]
body_excl = [m for m in body_ht_middles if m not in all_a_middles]

line1_pp = [m for m in line1_ht_middles if m in all_a_middles]
line1_excl = [m for m in line1_ht_middles if m not in all_a_middles]

print(f"\nBody HT:")
print(f"  PP: {len(body_pp)} ({100*len(body_pp)/len(body_ht_middles):.1f}%)")
print(f"  B-exclusive: {len(body_excl)} ({100*len(body_excl)/len(body_ht_middles):.1f}%)")

print(f"\nLine-1 HT:")
print(f"  PP: {len(line1_pp)} ({100*len(line1_pp)/len(line1_ht_middles):.1f}%)")
print(f"  B-exclusive: {len(line1_excl)} ({100*len(line1_excl)/len(line1_ht_middles):.1f}%)")

# Chi-squared for PP rate difference
contingency = [[len(body_pp), len(body_excl)],
               [len(line1_pp), len(line1_excl)]]
chi2, p_chi, _, _ = stats.chi2_contingency(contingency)
print(f"\nChi-squared (body vs line-1 PP rate): chi2={chi2:.1f}, p={p_chi:.4f}")

# ============================================================
# TEST 3: Vocabulary overlap
# ============================================================
print("\n" + "=" * 70)
print("TEST 3: LINE-1 vs BODY VOCABULARY OVERLAP")
print("=" * 70)

line1_types = set(line1_ht_middles)
body_types = set(body_ht_middles)

shared = line1_types & body_types
line1_only = line1_types - body_types
body_only = body_types - line1_types

print(f"\nLine-1 only: {len(line1_only)} types")
print(f"Body only: {len(body_only)} types")
print(f"Shared: {len(shared)} types")
print(f"Jaccard: {len(shared) / len(line1_types | body_types):.3f}")

# ============================================================
# TEST 4: Body HT by escape regime
# ============================================================
print("\n" + "=" * 70)
print("TEST 4: BODY HT BY ESCAPE REGIME")
print("=" * 70)

# Compute FL rate per folio
folio_fl_rates = {}
for folio, d in folio_fl.items():
    if d['classified'] > 0:
        folio_fl_rates[folio] = 100 * d['fl'] / d['classified']

# Split into high/low FL
fl_values = list(folio_fl_rates.values())
fl_median = np.median(fl_values)

low_fl_folios = [f for f, r in folio_fl_rates.items() if r < fl_median]
high_fl_folios = [f for f, r in folio_fl_rates.items() if r >= fl_median]

# Collect body HT MIDDLEs by regime
low_fl_middles = []
high_fl_middles = []

for folio in low_fl_folios:
    low_fl_middles.extend(body_ht_by_folio.get(folio, []))
for folio in high_fl_folios:
    high_fl_middles.extend(body_ht_by_folio.get(folio, []))

print(f"\nLow FL folios ({len(low_fl_folios)}): {len(low_fl_middles)} body HT MIDDLEs")
print(f"High FL folios ({len(high_fl_folios)}): {len(high_fl_middles)} body HT MIDDLEs")

# PP rate by regime
low_pp_rate = sum(1 for m in low_fl_middles if m in all_a_middles) / len(low_fl_middles) if low_fl_middles else 0
high_pp_rate = sum(1 for m in high_fl_middles if m in all_a_middles) / len(high_fl_middles) if high_fl_middles else 0

print(f"\nPP rate in body HT:")
print(f"  Low FL: {100*low_pp_rate:.1f}%")
print(f"  High FL: {100*high_pp_rate:.1f}%")

# Top MIDDLEs by regime
print(f"\nTop 10 body HT MIDDLEs in HIGH FL folios:")
high_counter = Counter(high_fl_middles)
for mid, count in high_counter.most_common(10):
    is_pp = "PP" if mid in all_a_middles else "B-excl"
    print(f"  '{mid}': {count} ({is_pp})")

print(f"\nTop 10 body HT MIDDLEs in LOW FL folios:")
low_counter = Counter(low_fl_middles)
for mid, count in low_counter.most_common(10):
    is_pp = "PP" if mid in all_a_middles else "B-excl"
    print(f"  '{mid}': {count} ({is_pp})")

# ============================================================
# TEST 5: Enriched MIDDLEs in high-escape context
# ============================================================
print("\n" + "=" * 70)
print("TEST 5: MIDDLES ENRICHED IN HIGH-ESCAPE CONTEXT")
print("=" * 70)

# Find MIDDLEs that are overrepresented in high-FL folios
all_body_middles = set(body_ht_middles)
enrichment = []

for mid in all_body_middles:
    low_count = low_counter.get(mid, 0)
    high_count = high_counter.get(mid, 0)

    if low_count + high_count < 5:
        continue

    # Expected under null
    total = low_count + high_count
    low_total = len(low_fl_middles)
    high_total = len(high_fl_middles)
    expected_high = total * high_total / (low_total + high_total)

    if expected_high > 0:
        enrichment.append({
            'middle': mid,
            'low': low_count,
            'high': high_count,
            'ratio': high_count / expected_high,
            'is_pp': mid in all_a_middles,
        })

# Sort by enrichment ratio
enrichment.sort(key=lambda x: x['ratio'], reverse=True)

print(f"\nMIDDLEs enriched in high-escape folios (ratio > 1.5):")
for e in enrichment[:15]:
    if e['ratio'] > 1.5:
        pp = "PP" if e['is_pp'] else "B-excl"
        print(f"  '{e['middle']}': {e['ratio']:.2f}x ({e['high']} high, {e['low']} low) [{pp}]")

print(f"\nMIDDLEs depleted in high-escape folios (ratio < 0.67):")
for e in sorted(enrichment, key=lambda x: x['ratio'])[:10]:
    if e['ratio'] < 0.67:
        pp = "PP" if e['is_pp'] else "B-excl"
        print(f"  '{e['middle']}': {e['ratio']:.2f}x ({e['high']} high, {e['low']} low) [{pp}]")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"""
BODY HT COMPOSITION:
  Total: {len(body_ht_middles)} tokens, {len(set(body_ht_middles))} types
  PP: {100*len(body_pp)/len(body_ht_middles):.1f}%
  B-exclusive: {100*len(body_excl)/len(body_ht_middles):.1f}%

COMPARISON TO LINE-1:
  Line-1 PP rate: {100*len(line1_pp)/len(line1_ht_middles):.1f}%
  Body PP rate: {100*len(body_pp)/len(body_ht_middles):.1f}%
  Difference: {100*(len(body_pp)/len(body_ht_middles) - len(line1_pp)/len(line1_ht_middles)):+.1f}pp

ESCAPE REGIME EFFECT:
  High FL body HT PP rate: {100*high_pp_rate:.1f}%
  Low FL body HT PP rate: {100*low_pp_rate:.1f}%
""")
