"""
T4: Classified vs UN Compound Rate Comparison

Question: Do UN (unclassified/HT) tokens show higher compound rates than
classified tokens? If so, this confirms UN = derived identification vocabulary.

Hypothesis: The 479 classified types represent "base grammar" while UN tokens
are "derived vocabulary" built combinatorially from core MIDDLEs.

Method:
1. Load classified token set (479 types from 49 classes)
2. Separate B tokens into classified vs UN
3. Extract MIDDLEs from each group
4. Compare compound rates, folio-uniqueness, length distributions
5. Test if UN is predominantly compound forms
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology, MiddleAnalyzer

tx = Transcript()
morph = Morphology()

# Load classified token set
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm = json.load(f)
classified_tokens = set(ctm['token_to_class'].keys())

print(f"Classified token types: {len(classified_tokens)}")

# Build MiddleAnalyzer for compound detection
mid_analyzer = MiddleAnalyzer()
mid_analyzer.build_inventory('B')

core_middles = mid_analyzer.get_core_middles()
print(f"Core MIDDLEs (20+ folios): {len(core_middles)}")

# Collect all B tokens with classification
classified_data = []
un_data = []

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    m = morph.extract(w)
    if not m.middle:
        continue

    entry = {
        'word': w,
        'middle': m.middle,
        'folio': token.folio,
        'line': token.line
    }

    if w in classified_tokens:
        classified_data.append(entry)
    else:
        un_data.append(entry)

print(f"\nToken counts:")
print(f"  Classified tokens: {len(classified_data)}")
print(f"  UN tokens: {len(un_data)}")
print(f"  UN fraction: {100*len(un_data)/(len(classified_data)+len(un_data)):.1f}%")

# Extract unique MIDDLEs from each group
classified_middles = set(d['middle'] for d in classified_data)
un_middles = set(d['middle'] for d in un_data)

print(f"\nUnique MIDDLEs:")
print(f"  Classified: {len(classified_middles)}")
print(f"  UN: {len(un_middles)}")

# Check overlap
overlap = classified_middles & un_middles
classified_only = classified_middles - un_middles
un_only = un_middles - classified_middles

print(f"\nMIDDLE overlap:")
print(f"  Shared: {len(overlap)}")
print(f"  Classified-only: {len(classified_only)}")
print(f"  UN-only: {len(un_only)}")

# Compound rate comparison
def get_compound_rate(middles, core_set, min_len=2):
    """Calculate compound rate for a set of MIDDLEs."""
    compound_count = 0
    for mid in middles:
        for core in core_set:
            if len(core) >= min_len and core in mid and core != mid:
                compound_count += 1
                break
    return 100 * compound_count / len(middles) if middles else 0

classified_compound_rate = get_compound_rate(classified_middles, core_middles)
un_compound_rate = get_compound_rate(un_middles, core_middles)

print(f"\n" + "="*60)
print("COMPOUND RATE COMPARISON")
print("="*60)
print(f"Classified MIDDLEs compound rate: {classified_compound_rate:.1f}%")
print(f"UN MIDDLEs compound rate: {un_compound_rate:.1f}%")
print(f"Difference: {un_compound_rate - classified_compound_rate:+.1f}pp")

# Folio-uniqueness comparison
def get_folio_spread(data_list):
    """Get MIDDLE -> folio set mapping."""
    mid_to_folios = defaultdict(set)
    for d in data_list:
        mid_to_folios[d['middle']].add(d['folio'])
    return mid_to_folios

classified_spread = get_folio_spread(classified_data)
un_spread = get_folio_spread(un_data)

classified_folio_unique = sum(1 for mid, folios in classified_spread.items() if len(folios) == 1)
un_folio_unique = sum(1 for mid, folios in un_spread.items() if len(folios) == 1)

classified_fu_rate = 100 * classified_folio_unique / len(classified_middles) if classified_middles else 0
un_fu_rate = 100 * un_folio_unique / len(un_middles) if un_middles else 0

print(f"\n" + "="*60)
print("FOLIO-UNIQUENESS COMPARISON")
print("="*60)
print(f"Classified folio-unique rate: {classified_folio_unique}/{len(classified_middles)} = {classified_fu_rate:.1f}%")
print(f"UN folio-unique rate: {un_folio_unique}/{len(un_middles)} = {un_fu_rate:.1f}%")
print(f"Difference: {un_fu_rate - classified_fu_rate:+.1f}pp")

# Length comparison
classified_lengths = [len(mid) for mid in classified_middles]
un_lengths = [len(mid) for mid in un_middles]

classified_mean_len = sum(classified_lengths) / len(classified_lengths) if classified_lengths else 0
un_mean_len = sum(un_lengths) / len(un_lengths) if un_lengths else 0

print(f"\n" + "="*60)
print("LENGTH COMPARISON")
print("="*60)
print(f"Classified mean MIDDLE length: {classified_mean_len:.2f}")
print(f"UN mean MIDDLE length: {un_mean_len:.2f}")
print(f"Difference: {un_mean_len - classified_mean_len:+.2f}")

# Length distribution
print(f"\nLength distribution:")
print(f"  {'Length':<8} {'Classified':<12} {'UN':<12}")
print(f"  {'-'*8} {'-'*12} {'-'*12}")
classified_len_dist = Counter(classified_lengths)
un_len_dist = Counter(un_lengths)
for length in range(1, 10):
    c_count = classified_len_dist.get(length, 0)
    u_count = un_len_dist.get(length, 0)
    c_pct = 100 * c_count / len(classified_middles) if classified_middles else 0
    u_pct = 100 * u_count / len(un_middles) if un_middles else 0
    print(f"  {length:<8} {c_count:>4} ({c_pct:>5.1f}%)  {u_count:>4} ({u_pct:>5.1f}%)")

# Compound rate by length (to control for length effect)
print(f"\n" + "="*60)
print("COMPOUND RATE BY LENGTH (length-controlled)")
print("="*60)

for length in range(2, 8):
    c_mids = [m for m in classified_middles if len(m) == length]
    u_mids = [m for m in un_middles if len(m) == length]

    if c_mids and u_mids:
        c_rate = get_compound_rate(c_mids, core_middles)
        u_rate = get_compound_rate(u_mids, core_middles)
        print(f"Length {length}: Classified={c_rate:.1f}% ({len(c_mids)}), UN={u_rate:.1f}% ({len(u_mids)}), diff={u_rate-c_rate:+.1f}pp")

# Check if UN-only MIDDLEs are more compound than shared MIDDLEs
shared_compound_rate = get_compound_rate(overlap, core_middles)
un_only_compound_rate = get_compound_rate(un_only, core_middles)
classified_only_compound_rate = get_compound_rate(classified_only, core_middles)

print(f"\n" + "="*60)
print("COMPOUND RATE BY EXCLUSIVITY")
print("="*60)
print(f"Shared MIDDLEs: {shared_compound_rate:.1f}% compound ({len(overlap)} types)")
print(f"Classified-only MIDDLEs: {classified_only_compound_rate:.1f}% compound ({len(classified_only)} types)")
print(f"UN-only MIDDLEs: {un_only_compound_rate:.1f}% compound ({len(un_only)} types)")

# Show examples
print(f"\n" + "="*60)
print("EXAMPLES")
print("="*60)

print(f"\nUN-only compound MIDDLEs (samples):")
un_only_compounds = [m for m in sorted(un_only, key=len, reverse=True)
                     if mid_analyzer.is_compound(m)][:10]
for mid in un_only_compounds:
    atoms = mid_analyzer.get_contained_atoms(mid)
    stats = mid_analyzer.get_stats(mid)
    fu = "FOLIO-UNIQUE" if stats and stats.is_folio_unique else ""
    print(f"  '{mid}' contains {atoms} {fu}")

print(f"\nClassified-only MIDDLEs (samples):")
for mid in sorted(classified_only, key=len, reverse=True)[:10]:
    is_cmp = mid_analyzer.is_compound(mid)
    atoms = mid_analyzer.get_contained_atoms(mid) if is_cmp else []
    print(f"  '{mid}' compound={is_cmp} {atoms}")

# Verdict
print(f"\n" + "="*60)
print("VERDICT")
print("="*60)

compound_diff = un_compound_rate - classified_compound_rate
fu_diff = un_fu_rate - classified_fu_rate
len_diff = un_mean_len - classified_mean_len

if compound_diff > 20 and fu_diff > 20:
    verdict = "STRONG_CONFIRMATION"
    explanation = f"UN tokens are dramatically more compound (+{compound_diff:.1f}pp) and folio-unique (+{fu_diff:.1f}pp). UN = derived identification vocabulary."
elif compound_diff > 10:
    verdict = "MODERATE_CONFIRMATION"
    explanation = f"UN tokens show elevated compound rate (+{compound_diff:.1f}pp). Partial support for derived vocabulary hypothesis."
elif compound_diff > 0:
    verdict = "WEAK_CONFIRMATION"
    explanation = f"UN shows slightly higher compound rate (+{compound_diff:.1f}pp) but effect is modest."
else:
    verdict = "NOT_CONFIRMED"
    explanation = f"UN does not show higher compound rate than classified. Hypothesis not supported."

print(f"\n{verdict}")
print(f"{explanation}")

# Additional insight
if un_only_compound_rate > 60:
    print(f"\nCRITICAL: UN-only MIDDLEs are {un_only_compound_rate:.1f}% compound.")
    print(f"These {len(un_only)} types appear ONLY in UN tokens, never in classified grammar.")
    print(f"This confirms they are derived forms, not base vocabulary.")

# Save results
results = {
    'token_counts': {
        'classified': len(classified_data),
        'un': len(un_data),
        'un_fraction': len(un_data) / (len(classified_data) + len(un_data))
    },
    'middle_counts': {
        'classified': len(classified_middles),
        'un': len(un_middles),
        'shared': len(overlap),
        'classified_only': len(classified_only),
        'un_only': len(un_only)
    },
    'compound_rates': {
        'classified': classified_compound_rate,
        'un': un_compound_rate,
        'difference': compound_diff,
        'shared': shared_compound_rate,
        'classified_only': classified_only_compound_rate,
        'un_only': un_only_compound_rate
    },
    'folio_unique_rates': {
        'classified': classified_fu_rate,
        'un': un_fu_rate,
        'difference': fu_diff
    },
    'length': {
        'classified_mean': classified_mean_len,
        'un_mean': un_mean_len,
        'difference': len_diff
    },
    'verdict': verdict
}

out_path = PROJECT_ROOT / 'phases' / 'COMPOUND_MIDDLE_ARCHITECTURE' / 'results' / 't4_classified_compound.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path}")
