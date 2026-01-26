"""
Q1: AUXILIARY Census Reconciliation

Establish the definitive AX class membership by reconciling three taxonomies:
- BCSC contract: AX = 1-6, 15-22, 24-29 (20 classes)
- ICC (INSTRUCTION_CLASS_CHARACTERIZATION) RESULTS.md
- CSV (CLASS_SEMANTIC_VALIDATION) simplified ROLE_MAP

Also produces per-class token counts for the definitive AX set.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict
from scripts.voynich import Transcript

# Paths
BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
RESULTS = BASE / 'phases/AUXILIARY_STRATIFICATION/results'

# Load data
tx = Transcript()
tokens = list(tx.currier_b())

with open(CLASS_MAP) as f:
    class_data = json.load(f)

token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}

# Invert: class -> tokens
class_to_tokens = defaultdict(list)
for tok, cls in token_to_class.items():
    class_to_tokens[cls].append(tok)

ALL_CLASSES = set(token_to_class.values())

# ============================================================
# THREE TAXONOMIES
# ============================================================

# 1. BCSC contract: explicit range
BCSC_AX = set(range(1, 7)) | set(range(15, 23)) | set(range(24, 30))  # 1-6, 15-22, 24-29
BCSC_CC = {10, 11, 12}
BCSC_EN = set()  # 11 classes, not enumerated in BCSC
BCSC_FL = set()  # 2 classes per BCSC
BCSC_FQ = set()  # 4 classes per BCSC
BCSC_HI = set()  # 3 classes per BCSC

# 2. ICC (from RESULTS.md): full enumeration
ICC_CC = {10, 11, 12}
ICC_EN = {8} | set(range(31, 50))  # 8, 31-49 (ch/sh + qo families) = 20 classes
ICC_FL = {7, 30, 38, 40}
ICC_FQ = {9, 13, 23}  # 14 is ambiguous
ICC_AX = ALL_CLASSES - ICC_CC - ICC_EN - ICC_FL - ICC_FQ

# 3. CSV (simplified ROLE_MAP from phase scripts)
CSV_CC = {10, 11, 17}
CSV_EN = {8, 31, 32, 33, 34, 36}
CSV_FL = {7, 30, 38, 40}
CSV_FQ = {9, 20, 21, 23}
CSV_AX = ALL_CLASSES - CSV_CC - CSV_EN - CSV_FL - CSV_FQ

print("=" * 70)
print("Q1: AUXILIARY CENSUS RECONCILIATION")
print("=" * 70)

# ============================================================
# TAXONOMY COMPARISON
# ============================================================
print("\n" + "-" * 70)
print("1. TAXONOMY SIZES")
print("-" * 70)

print(f"\n{'Taxonomy':<10} {'CC':>4} {'EN':>4} {'FL':>4} {'FQ':>4} {'HI':>4} {'AX':>4} {'Total':>6}")
print(f"{'BCSC':<10} {len(BCSC_CC):>4} {'11':>4} {'2':>4} {'4':>4} {'3':>4} {len(BCSC_AX):>4} {'49':>6}")
print(f"{'ICC':<10} {len(ICC_CC):>4} {len(ICC_EN):>4} {len(ICC_FL):>4} {len(ICC_FQ):>4} {'-':>4} {len(ICC_AX):>4} {len(ALL_CLASSES):>6}")
print(f"{'CSV':<10} {len(CSV_CC):>4} {len(CSV_EN):>4} {len(CSV_FL):>4} {len(CSV_FQ):>4} {'-':>4} {len(CSV_AX):>4} {len(ALL_CLASSES):>6}")

# ============================================================
# DISCREPANCY ANALYSIS
# ============================================================
print("\n" + "-" * 70)
print("2. CLASS-BY-CLASS DISCREPANCY REPORT")
print("-" * 70)

def get_role(cls, cc, en, fl, fq, ax_set):
    if cls in cc: return 'CC'
    if cls in en: return 'EN'
    if cls in fl: return 'FL'
    if cls in fq: return 'FQ'
    if cls in ax_set: return 'AX'
    return '??'

print(f"\n{'Class':>5} {'BCSC':>6} {'ICC':>6} {'CSV':>6} {'Conflict?':>10}")
discrepancies = []
for cls in sorted(ALL_CLASSES):
    bcsc_role = get_role(cls, BCSC_CC, set(), set(), set(), BCSC_AX)
    if cls not in BCSC_CC and cls not in BCSC_AX:
        bcsc_role = 'other'  # Not enumerated

    icc_role = get_role(cls, ICC_CC, ICC_EN, ICC_FL, ICC_FQ, ICC_AX)
    csv_role = get_role(cls, CSV_CC, CSV_EN, CSV_FL, CSV_FQ, CSV_AX)

    conflict = icc_role != csv_role
    if conflict:
        discrepancies.append((cls, bcsc_role, icc_role, csv_role))

    marker = '***' if conflict else ''
    print(f"{cls:5d} {bcsc_role:>6} {icc_role:>6} {csv_role:>6} {marker:>10}")

print(f"\nTotal discrepancies between ICC and CSV: {len(discrepancies)}")

# ============================================================
# SPECIFIC DISCREPANCY CASES
# ============================================================
print("\n" + "-" * 70)
print("3. SPECIFIC DISCREPANCY CASES")
print("-" * 70)

for cls, bcsc, icc, csv in discrepancies:
    toks = sorted(class_to_tokens.get(cls, []))[:5]
    tok_str = ', '.join(toks) + ('...' if len(class_to_tokens.get(cls, [])) > 5 else '')
    print(f"\nClass {cls}: ICC={icc}, CSV={csv}, BCSC={bcsc}")
    print(f"  Tokens ({len(class_to_tokens.get(cls, []))}): {tok_str}")

    if cls == 17:
        print("  NOTE: C560 says 'ol-derived control operators' -> classified as CC")
        print("  BCSC range 15-22 includes this class -> classified as AX")
    elif cls in {13, 14}:
        print(f"  NOTE: ICC classifies as FQ (okaiin/okeey family)")
        print(f"  CSV does not include in FQ map -> defaults to AX")
    elif cls in {20, 21}:
        print(f"  NOTE: CSV classifies as FQ")
        print(f"  BCSC range 15-22 includes this -> AX")
        print(f"  ICC does not classify as FQ -> AX")

# ============================================================
# DEFINITIVE AX SET (using ICC as authoritative)
# ============================================================
print("\n" + "-" * 70)
print("4. DEFINITIVE AX CLASS SET (ICC taxonomy)")
print("-" * 70)

# Use ICC taxonomy as it's the most complete empirical classification
# Note: Class 17 dispute (CC per C560 vs AX per BCSC) - follow C560
DEFINITIVE_AX = ICC_AX.copy()
# Class 17: C560 explicitly reclassified it as CC (ol-derived control operators)
# Remove from AX if it ended up there via ICC
if 17 in DEFINITIVE_AX:
    print(f"Class 17 is in ICC_AX={17 in ICC_AX} -> removing per C560 (CC)")
    DEFINITIVE_AX.discard(17)

print(f"\nDefinitive AX classes ({len(DEFINITIVE_AX)}): {sorted(DEFINITIVE_AX)}")

# ============================================================
# PER-CLASS TOKEN CENSUS
# ============================================================
print("\n" + "-" * 70)
print("5. AX PER-CLASS TOKEN CENSUS")
print("-" * 70)

# Count actual occurrences in corpus
class_counts = defaultdict(int)
for token in tokens:
    word = token.word.replace('*', '').strip()
    cls = token_to_class.get(word)
    if cls is not None:
        class_counts[cls] += 1

total_b_classified = sum(class_counts.values())
ax_total = sum(class_counts.get(c, 0) for c in DEFINITIVE_AX)

print(f"\nTotal classified B tokens: {total_b_classified}")
print(f"Total AX tokens: {ax_total} ({ax_total/total_b_classified*100:.1f}%)")

print(f"\n{'Class':>5} {'Types':>6} {'Tokens':>7} {'% of AX':>8} {'% of B':>7} {'Top tokens'}")
for cls in sorted(DEFINITIVE_AX):
    types = class_to_tokens.get(cls, [])
    count = class_counts.get(cls, 0)
    pct_ax = count / ax_total * 100 if ax_total > 0 else 0
    pct_b = count / total_b_classified * 100 if total_b_classified > 0 else 0
    top = sorted(types, key=lambda t: -sum(1 for tk in tokens if tk.word.replace('*', '').strip() == t))[:3]
    print(f"{cls:5d} {len(types):6d} {count:7d} {pct_ax:7.1f}% {pct_b:6.1f}% {', '.join(top)}")

# ============================================================
# ICC PREFIX FAMILIES
# ============================================================
print("\n" + "-" * 70)
print("6. ICC PREFIX FAMILIES WITHIN AX")
print("-" * 70)

# Classify AX classes by dominant prefix
from scripts.voynich import Morphology
morph = Morphology()

class_prefix_profile = {}
for cls in sorted(DEFINITIVE_AX):
    types = class_to_tokens.get(cls, [])
    prefix_counts = defaultdict(int)
    artic_count = 0
    for t in types:
        m = morph.extract(t)
        prefix_counts[m.prefix or 'NONE'] += 1
        if m.has_articulator:
            artic_count += 1

    dominant_prefix = max(prefix_counts, key=prefix_counts.get) if prefix_counts else 'NONE'
    artic_rate = artic_count / len(types) if types else 0
    class_prefix_profile[cls] = {
        'dominant_prefix': dominant_prefix,
        'prefix_counts': dict(prefix_counts),
        'articulator_rate': artic_rate,
        'n_types': len(types)
    }

    prefix_str = ', '.join(f"{p}:{c}" for p, c in sorted(prefix_counts.items(), key=lambda x: -x[1])[:3])
    print(f"Class {cls:3d}: dominant={dominant_prefix:6s} artic={artic_rate:.0%} [{prefix_str}]")

# Group by family
families = defaultdict(list)
for cls, profile in class_prefix_profile.items():
    dp = profile['dominant_prefix']
    ar = profile['articulator_rate']
    if ar > 0.3:
        families['ARTICULATED'].append(cls)
    elif dp in ('ok', 'ot'):
        families['OK/OT'].append(cls)
    elif dp == 'ol':
        families['OL'].append(cls)
    elif dp in ('ch', 'sh'):
        families['CH/SH'].append(cls)
    elif dp == 'd':
        families['D'].append(cls)
    else:
        families[f'OTHER({dp})'].append(cls)

print(f"\nPrefix families:")
for fam, classes in sorted(families.items()):
    print(f"  {fam}: {sorted(classes)}")

# ============================================================
# SAVE RESULTS
# ============================================================
results = {
    'definitive_ax_classes': sorted(DEFINITIVE_AX),
    'definitive_ax_count': len(DEFINITIVE_AX),
    'ax_token_total': ax_total,
    'ax_pct_of_b': round(ax_total / total_b_classified * 100, 1) if total_b_classified > 0 else 0,
    'total_classified_b': total_b_classified,
    'per_class': {
        str(cls): {
            'types': len(class_to_tokens.get(cls, [])),
            'tokens': class_counts.get(cls, 0),
            'pct_of_ax': round(class_counts.get(cls, 0) / ax_total * 100, 1) if ax_total > 0 else 0,
            'prefix_profile': class_prefix_profile.get(cls, {})
        }
        for cls in sorted(DEFINITIVE_AX)
    },
    'prefix_families': {fam: sorted(cls_list) for fam, cls_list in families.items()},
    'discrepancies': [
        {'class': cls, 'bcsc': bcsc, 'icc': icc, 'csv': csv}
        for cls, bcsc, icc, csv in discrepancies
    ],
    'taxonomy_comparison': {
        'icc_ax': sorted(ICC_AX),
        'csv_ax': sorted(CSV_AX),
        'bcsc_ax': sorted(BCSC_AX),
        'icc_en': sorted(ICC_EN),
        'csv_en': sorted(CSV_EN),
    }
}

with open(RESULTS / 'ax_census.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults saved to {RESULTS / 'ax_census.json'}")
