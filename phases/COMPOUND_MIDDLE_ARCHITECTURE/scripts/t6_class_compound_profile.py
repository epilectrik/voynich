"""
T6: Class-Level Compound Profile

Question: Which instruction classes use base MIDDLEs vs compound MIDDLEs?
Does this correlate with kernel operators (k, h, e) or other functional roles?

The T5 finding showed dramatic class-level variation:
- Classes 31, 32, 14: 0% compound (pure base)
- Classes 8, 13, 29: 80-90% compound

This test systematically profiles all 49 classes.
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

# Load classified token set with class info
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm = json.load(f)

token_to_class = ctm['token_to_class']
classified_tokens = set(token_to_class.keys())

# Build MiddleAnalyzer
mid_analyzer = MiddleAnalyzer()
mid_analyzer.build_inventory('B')
core_middles = mid_analyzer.get_core_middles()

print(f"Core MIDDLEs: {len(core_middles)}")
print(f"Classified types: {len(classified_tokens)}")

# Collect all classified B tokens with their class and compound status
class_data = defaultdict(list)

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    if w not in classified_tokens:
        continue

    m = morph.extract(w)
    if not m.middle:
        continue

    cls = token_to_class[w]
    is_compound = mid_analyzer.is_compound(m.middle)

    class_data[cls].append({
        'word': w,
        'middle': m.middle,
        'is_compound': is_compound,
        'middle_length': len(m.middle)
    })

print(f"Classes with data: {len(class_data)}")

# ============================================================
# ANALYSIS: Compound profile per class
# ============================================================
print("\n" + "="*70)
print("CLASS COMPOUND PROFILES (sorted by compound rate)")
print("="*70)

class_profiles = []

for cls, tokens in class_data.items():
    total = len(tokens)
    compound = sum(1 for t in tokens if t['is_compound'])
    compound_rate = 100 * compound / total if total else 0

    # Get unique MIDDLEs in this class
    middles = set(t['middle'] for t in tokens)
    unique_types = len(set(t['word'] for t in tokens))

    # Mean MIDDLE length
    mean_len = sum(t['middle_length'] for t in tokens) / total if total else 0

    class_profiles.append({
        'class': cls,
        'total_tokens': total,
        'unique_types': unique_types,
        'unique_middles': len(middles),
        'compound_count': compound,
        'compound_rate': compound_rate,
        'mean_middle_length': mean_len,
        'middles': list(middles)
    })

# Sort by compound rate
class_profiles.sort(key=lambda x: x['compound_rate'])

print(f"\n{'Class':<8} {'Tokens':<8} {'Types':<8} {'MIDDLEs':<8} {'Compound%':<12} {'MeanLen':<8}")
print("-" * 70)

for p in class_profiles:
    print(f"{p['class']:<8} {p['total_tokens']:<8} {p['unique_types']:<8} {p['unique_middles']:<8} {p['compound_rate']:<12.1f} {p['mean_middle_length']:<8.2f}")

# ============================================================
# IDENTIFY BASE-ONLY vs COMPOUND-HEAVY CLASSES
# ============================================================
print("\n" + "="*70)
print("CLASS CATEGORIZATION")
print("="*70)

base_only = [p for p in class_profiles if p['compound_rate'] < 5]
low_compound = [p for p in class_profiles if 5 <= p['compound_rate'] < 30]
medium_compound = [p for p in class_profiles if 30 <= p['compound_rate'] < 60]
high_compound = [p for p in class_profiles if 60 <= p['compound_rate'] < 85]
compound_heavy = [p for p in class_profiles if p['compound_rate'] >= 85]

print(f"\nBASE-ONLY (0-5% compound): {len(base_only)} classes")
for p in base_only:
    mids = ', '.join(sorted(p['middles'])[:5])
    print(f"  Class {p['class']}: {p['compound_rate']:.1f}% ({p['total_tokens']} tok) MIDDLEs: {mids}...")

print(f"\nLOW COMPOUND (5-30%): {len(low_compound)} classes")
for p in low_compound:
    mids = ', '.join(sorted(p['middles'])[:5])
    print(f"  Class {p['class']}: {p['compound_rate']:.1f}% ({p['total_tokens']} tok)")

print(f"\nMEDIUM COMPOUND (30-60%): {len(medium_compound)} classes")
for p in medium_compound:
    print(f"  Class {p['class']}: {p['compound_rate']:.1f}% ({p['total_tokens']} tok)")

print(f"\nHIGH COMPOUND (60-85%): {len(high_compound)} classes")
for p in high_compound:
    print(f"  Class {p['class']}: {p['compound_rate']:.1f}% ({p['total_tokens']} tok)")

print(f"\nCOMPOUND-HEAVY (85%+): {len(compound_heavy)} classes")
for p in compound_heavy:
    mids = ', '.join(sorted(p['middles'], key=len, reverse=True)[:5])
    print(f"  Class {p['class']}: {p['compound_rate']:.1f}% ({p['total_tokens']} tok) MIDDLEs: {mids}...")

# ============================================================
# ANALYZE MIDDLE STRUCTURE IN BASE-ONLY CLASSES
# ============================================================
print("\n" + "="*70)
print("BASE-ONLY CLASS MIDDLE ANALYSIS")
print("="*70)

print("\nThese classes use MIDDLEs that are NOT compound (don't contain core MIDDLEs):")
base_class_middles = set()
for p in base_only:
    base_class_middles.update(p['middles'])

print(f"\nTotal unique MIDDLEs in base-only classes: {len(base_class_middles)}")
print(f"Sample MIDDLEs: {sorted(base_class_middles, key=len)[:20]}")

# Are these base-only MIDDLEs themselves the core MIDDLEs?
in_core = sum(1 for m in base_class_middles if m in core_middles)
print(f"\nBase-only MIDDLEs that ARE core MIDDLEs: {in_core}/{len(base_class_middles)} ({100*in_core/len(base_class_middles):.1f}%)")

# ============================================================
# ANALYZE MIDDLE STRUCTURE IN COMPOUND-HEAVY CLASSES
# ============================================================
print("\n" + "="*70)
print("COMPOUND-HEAVY CLASS MIDDLE ANALYSIS")
print("="*70)

compound_class_middles = set()
for p in compound_heavy:
    compound_class_middles.update(p['middles'])

print(f"\nTotal unique MIDDLEs in compound-heavy classes: {len(compound_class_middles)}")

# What cores do they contain?
core_usage = Counter()
for mid in compound_class_middles:
    atoms = mid_analyzer.get_contained_atoms(mid)
    for atom in atoms:
        core_usage[atom] += 1

print(f"\nMost common core atoms in compound-heavy classes:")
for atom, count in core_usage.most_common(15):
    print(f"  '{atom}': {count} occurrences")

# ============================================================
# CROSS-REFERENCE: Do base-only MIDDLEs seed compound-heavy MIDDLEs?
# ============================================================
print("\n" + "="*70)
print("BASE -> COMPOUND DERIVATION CHECK")
print("="*70)

# Check if base-only MIDDLEs appear as substrings in compound-heavy MIDDLEs
base_in_compound = 0
base_seeds = []
for base_mid in base_class_middles:
    if len(base_mid) >= 2:
        for comp_mid in compound_class_middles:
            if base_mid in comp_mid and base_mid != comp_mid:
                base_in_compound += 1
                base_seeds.append(base_mid)
                break

print(f"\nBase-only MIDDLEs that appear in compound-heavy MIDDLEs: {base_in_compound}/{len(base_class_middles)}")
print(f"  ({100*base_in_compound/len(base_class_middles):.1f}% of base-only MIDDLEs seed compound forms)")

if base_seeds:
    print(f"\nSeeding MIDDLEs: {sorted(set(base_seeds))[:15]}")

# ============================================================
# TOKEN COUNT DISTRIBUTION
# ============================================================
print("\n" + "="*70)
print("TOKEN COUNT BY COMPOUND CATEGORY")
print("="*70)

base_tokens = sum(p['total_tokens'] for p in base_only)
low_tokens = sum(p['total_tokens'] for p in low_compound)
med_tokens = sum(p['total_tokens'] for p in medium_compound)
high_tokens = sum(p['total_tokens'] for p in high_compound)
heavy_tokens = sum(p['total_tokens'] for p in compound_heavy)
total_tokens = base_tokens + low_tokens + med_tokens + high_tokens + heavy_tokens

print(f"\nBase-only classes: {len(base_only)} classes, {base_tokens} tokens ({100*base_tokens/total_tokens:.1f}%)")
print(f"Low compound: {len(low_compound)} classes, {low_tokens} tokens ({100*low_tokens/total_tokens:.1f}%)")
print(f"Medium compound: {len(medium_compound)} classes, {med_tokens} tokens ({100*med_tokens/total_tokens:.1f}%)")
print(f"High compound: {len(high_compound)} classes, {high_tokens} tokens ({100*high_tokens/total_tokens:.1f}%)")
print(f"Compound-heavy: {len(compound_heavy)} classes, {heavy_tokens} tokens ({100*heavy_tokens/total_tokens:.1f}%)")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT")
print("="*70)

if len(base_only) >= 3 and len(compound_heavy) >= 3:
    print("\nCLASS BIMODALITY CONFIRMED:")
    print(f"  - {len(base_only)} classes are BASE-ONLY (0-5% compound)")
    print(f"  - {len(compound_heavy)} classes are COMPOUND-HEAVY (85%+ compound)")
    print(f"  - The 49-class grammar has TWO functional vocabularies")

    if base_in_compound / len(base_class_middles) > 0.5:
        print(f"\nDERIVATION CONFIRMED:")
        print(f"  - {100*base_in_compound/len(base_class_middles):.1f}% of base-only MIDDLEs seed compound forms")
        print(f"  - Base classes provide atoms; compound classes use derived forms")
        verdict = "BIMODAL_WITH_DERIVATION"
    else:
        verdict = "BIMODAL_INDEPENDENT"
else:
    verdict = "NO_CLEAR_BIMODALITY"

print(f"\nVerdict: {verdict}")

# Save results
results = {
    'class_profiles': [{k: v for k, v in p.items() if k != 'middles'} for p in class_profiles],
    'categories': {
        'base_only': [p['class'] for p in base_only],
        'low_compound': [p['class'] for p in low_compound],
        'medium_compound': [p['class'] for p in medium_compound],
        'high_compound': [p['class'] for p in high_compound],
        'compound_heavy': [p['class'] for p in compound_heavy]
    },
    'token_distribution': {
        'base_only': base_tokens,
        'low_compound': low_tokens,
        'medium_compound': med_tokens,
        'high_compound': high_tokens,
        'compound_heavy': heavy_tokens
    },
    'derivation': {
        'base_middles_count': len(base_class_middles),
        'base_seeds_compound': base_in_compound,
        'seed_rate': base_in_compound / len(base_class_middles) if base_class_middles else 0
    },
    'verdict': verdict
}

out_path = PROJECT_ROOT / 'phases' / 'COMPOUND_MIDDLE_ARCHITECTURE' / 'results' / 't6_class_compound_profile.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path}")
