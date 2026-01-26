"""
Script 1: EN Census Reconciliation and MIDDLE Inventory

Establish definitive EN membership by reconciling three taxonomies.
Produce per-class token counts, MIDDLE inventory, and cross-role sharing.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict
from scripts.voynich import Transcript, Morphology

BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
MIDDLE_CLASSES = BASE / 'phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json'
AX_CENSUS = BASE / 'phases/AUXILIARY_STRATIFICATION/results/ax_census.json'
RESULTS = BASE / 'phases/EN_ANATOMY/results'

# Load data
tx = Transcript()
morph = Morphology()
tokens = list(tx.currier_b())

with open(CLASS_MAP) as f:
    class_data = json.load(f)
with open(MIDDLE_CLASSES) as f:
    mc = json.load(f)
with open(AX_CENSUS) as f:
    ax_data = json.load(f)

ri_middles = set(mc['a_exclusive_middles'])
pp_middles = set(mc['a_shared_middles'])

token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}
ALL_CLASSES = set(token_to_class.values())

# Invert: class -> tokens
class_to_tokens = defaultdict(list)
for tok, cls in token_to_class.items():
    class_to_tokens[cls].append(tok)

# ============================================================
# THREE TAXONOMIES
# ============================================================

# 1. BCSC contract: "11 classes" (not enumerated)
BCSC_EN_COUNT = 11

# 2. ICC (from INSTRUCTION_CLASS_CHARACTERIZATION)
# ICC assigns {8} | range(31,50) to EN, but FL gets {7, 30, 38, 40}
ICC_EN_RAW = {8} | set(range(31, 50))
ICC_FL = {7, 30, 38, 40}
ICC_CC = {10, 11, 12}
ICC_FQ = {9, 13, 23}
ICC_EN = (ICC_EN_RAW - ICC_FL) & ALL_CLASSES  # Remove FL, intersect with existing

# 3. CSV (simplified ROLE_MAP used in phase scripts)
CSV_EN = {8, 31, 32, 33, 34, 36}

# AX classes (from AUXILIARY_STRATIFICATION)
AX_CLASSES = {1, 2, 3, 4, 5, 6, 14, 15, 16, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29}

# Definitive EN = ICC-based (most comprehensive)
EN_CLASSES = ICC_EN

def get_role(cls_id):
    if cls_id in ICC_CC: return 'CC'
    if cls_id in ICC_FL: return 'FL'
    if cls_id in ICC_FQ: return 'FQ'
    if cls_id in AX_CLASSES: return 'AX'
    if cls_id in EN_CLASSES: return 'EN'
    return 'UNKNOWN'

print("=" * 70)
print("EN CENSUS RECONCILIATION AND MIDDLE INVENTORY")
print("=" * 70)

# ============================================================
# TAXONOMY COMPARISON
# ============================================================
print("\n" + "-" * 70)
print("1. TAXONOMY COMPARISON")
print("-" * 70)

icc_only = ICC_EN - CSV_EN
csv_only = CSV_EN - ICC_EN
shared = ICC_EN & CSV_EN

print(f"\nICC EN classes ({len(ICC_EN)}): {sorted(ICC_EN)}")
print(f"CSV EN classes ({len(CSV_EN)}): {sorted(CSV_EN)}")
print(f"Shared: {sorted(shared)}")
print(f"ICC-only (not in CSV): {sorted(icc_only)}")
print(f"CSV-only (not in ICC): {sorted(csv_only)}")
print(f"BCSC says: {BCSC_EN_COUNT} classes (not enumerated)")

# Classify into prefix families
QO_FAMILY = set()
CH_SH_FAMILY = set()
MINOR_FAMILY = set()

# Determine prefix family for each EN class
class_prefix_counts = defaultdict(lambda: defaultdict(int))
for tok, cls in token_to_class.items():
    if cls not in EN_CLASSES:
        continue
    m = morph.extract(tok)
    prefix = m.prefix if m.prefix else 'NONE'
    class_prefix_counts[cls][prefix] += 1

for cls in sorted(EN_CLASSES):
    prefixes = class_prefix_counts[cls]
    if not prefixes:
        MINOR_FAMILY.add(cls)
        continue
    dominant = max(prefixes, key=prefixes.get)
    total = sum(prefixes.values())
    dom_pct = prefixes[dominant] / total * 100

    if dominant in ('qo',):
        QO_FAMILY.add(cls)
    elif dominant in ('ch', 'sh'):
        CH_SH_FAMILY.add(cls)
    else:
        MINOR_FAMILY.add(cls)

print(f"\nPrefix families:")
print(f"  QO family ({len(QO_FAMILY)}): {sorted(QO_FAMILY)}")
print(f"  CH/SH family ({len(CH_SH_FAMILY)}): {sorted(CH_SH_FAMILY)}")
print(f"  MINOR family ({len(MINOR_FAMILY)}): {sorted(MINOR_FAMILY)}")

# ============================================================
# PER-CLASS TOKEN COUNTS
# ============================================================
print("\n" + "-" * 70)
print("2. PER-CLASS TOKEN COUNTS")
print("-" * 70)

# Count from corpus
class_corpus_counts = defaultdict(int)
for t in tokens:
    cls = token_to_class.get(t.word)
    if cls is not None and cls in EN_CLASSES:
        class_corpus_counts[cls] += 1

en_total = sum(class_corpus_counts.values())
b_total = len(tokens)

print(f"\nTotal EN tokens: {en_total} ({en_total/b_total*100:.1f}% of B)")
print(f"\n{'Class':>6} {'Types':>6} {'Tokens':>7} {'Pct':>6} {'Family':>8} {'Dom.Prefix':>12}")
print("-" * 50)

per_class = {}
for cls in sorted(EN_CLASSES):
    types = len(class_to_tokens[cls])
    count = class_corpus_counts[cls]
    pct = count / en_total * 100 if en_total > 0 else 0

    prefixes = class_prefix_counts[cls]
    dominant = max(prefixes, key=prefixes.get) if prefixes else 'NONE'

    if cls in QO_FAMILY:
        fam = 'QO'
    elif cls in CH_SH_FAMILY:
        fam = 'CH_SH'
    else:
        fam = 'MINOR'

    print(f"{cls:>6} {types:>6} {count:>7} {pct:>5.1f}% {fam:>8} {dominant:>12}")

    per_class[str(cls)] = {
        'types': types,
        'tokens': count,
        'pct_of_en': round(pct, 2),
        'family': fam,
        'dominant_prefix': dominant,
        'prefix_distribution': dict(prefixes)
    }

# Core vs minor
core_tokens = sum(class_corpus_counts[c] for c in CSV_EN)
minor_tokens = en_total - core_tokens
print(f"\nCore 6 classes: {core_tokens} tokens ({core_tokens/en_total*100:.1f}% of EN)")
print(f"Minor 12 classes: {minor_tokens} tokens ({minor_tokens/en_total*100:.1f}% of EN)")

# ============================================================
# MIDDLE INVENTORY
# ============================================================
print("\n" + "-" * 70)
print("3. MIDDLE INVENTORY")
print("-" * 70)

# Build class -> middles mapping
class_to_middles = defaultdict(set)
middle_to_classes = defaultdict(set)

for tok, cls in token_to_class.items():
    m = morph.extract(tok)
    mid = m.middle if m.middle else None
    if mid and cls in EN_CLASSES:
        class_to_middles[cls].add(mid)
        middle_to_classes[mid].add(cls)

all_en_middles = set()
for cls in EN_CLASSES:
    all_en_middles |= class_to_middles[cls]

# Classify MIDDLEs
pp_count = len(all_en_middles & pp_middles)
ri_count = len(all_en_middles & ri_middles)
b_exclusive = all_en_middles - pp_middles - ri_middles
b_exclusive_count = len(b_exclusive)

print(f"\nTotal unique EN MIDDLEs: {len(all_en_middles)}")
print(f"  PP (pipeline-participating): {pp_count} ({pp_count/len(all_en_middles)*100:.1f}%)")
print(f"  RI (registry-internal): {ri_count} ({ri_count/len(all_en_middles)*100:.1f}%)")
print(f"  B-exclusive: {b_exclusive_count} ({b_exclusive_count/len(all_en_middles)*100:.1f}%)")

# Cross-role sharing
role_middles = defaultdict(set)
for tok, cls in token_to_class.items():
    m = morph.extract(tok)
    mid = m.middle if m.middle else None
    if mid:
        role = get_role(cls)
        role_middles[role].add(mid)

print(f"\nCross-role MIDDLE sharing:")
for role in ['AX', 'CC', 'FL', 'FQ']:
    shared_m = all_en_middles & role_middles[role]
    union_m = all_en_middles | role_middles[role]
    jaccard = len(shared_m) / len(union_m) if union_m else 0
    print(f"  EN & {role}: {len(shared_m)} shared, Jaccard={jaccard:.3f}")

# EN-exclusive MIDDLEs
en_exclusive = all_en_middles.copy()
for role in ['AX', 'CC', 'FL', 'FQ']:
    en_exclusive -= role_middles[role]
print(f"\nEN-exclusive MIDDLEs: {len(en_exclusive)} ({len(en_exclusive)/len(all_en_middles)*100:.1f}%)")
if en_exclusive:
    print(f"  Examples: {sorted(en_exclusive)[:15]}")

# Per-family MIDDLE comparison
qo_middles = set()
chsh_middles = set()
for cls in QO_FAMILY:
    qo_middles |= class_to_middles[cls]
for cls in CH_SH_FAMILY:
    chsh_middles |= class_to_middles[cls]

shared_fam = qo_middles & chsh_middles
print(f"\nQO-family MIDDLEs: {len(qo_middles)}")
print(f"CH/SH-family MIDDLEs: {len(chsh_middles)}")
print(f"Shared between families: {len(shared_fam)}")
if qo_middles | chsh_middles:
    fam_jaccard = len(shared_fam) / len(qo_middles | chsh_middles)
    print(f"Inter-family Jaccard: {fam_jaccard:.3f}")

# ============================================================
# SAVE RESULTS
# ============================================================

results = {
    'definitive_en_classes': sorted(EN_CLASSES),
    'definitive_en_count': len(EN_CLASSES),
    'en_token_total': en_total,
    'en_pct_of_b': round(en_total / b_total * 100, 2),
    'b_total': b_total,
    'taxonomy_comparison': {
        'bcsc_count': BCSC_EN_COUNT,
        'icc_count': len(ICC_EN),
        'csv_count': len(CSV_EN),
        'icc_classes': sorted(ICC_EN),
        'csv_classes': sorted(CSV_EN),
        'icc_only': sorted(icc_only),
        'shared': sorted(shared)
    },
    'prefix_families': {
        'QO': sorted(QO_FAMILY),
        'CH_SH': sorted(CH_SH_FAMILY),
        'MINOR': sorted(MINOR_FAMILY)
    },
    'per_class': per_class,
    'core_vs_minor': {
        'core_classes': sorted(CSV_EN),
        'core_tokens': core_tokens,
        'core_pct': round(core_tokens / en_total * 100, 2),
        'minor_tokens': minor_tokens,
        'minor_pct': round(minor_tokens / en_total * 100, 2)
    },
    'middle_inventory': {
        'total_middles': len(all_en_middles),
        'pp_count': pp_count,
        'pp_pct': round(pp_count / len(all_en_middles) * 100, 2),
        'ri_count': ri_count,
        'ri_pct': round(ri_count / len(all_en_middles) * 100, 2),
        'b_exclusive_count': b_exclusive_count,
        'b_exclusive_pct': round(b_exclusive_count / len(all_en_middles) * 100, 2),
        'en_exclusive_count': len(en_exclusive),
        'en_exclusive_middles': sorted(en_exclusive),
        'cross_role_sharing': {
            role: {
                'shared': len(all_en_middles & role_middles[role]),
                'jaccard': round(len(all_en_middles & role_middles[role]) / len(all_en_middles | role_middles[role]), 4) if (all_en_middles | role_middles[role]) else 0
            }
            for role in ['AX', 'CC', 'FL', 'FQ']
        },
        'inter_family': {
            'qo_middles': len(qo_middles),
            'chsh_middles': len(chsh_middles),
            'shared': len(shared_fam),
            'jaccard': round(len(shared_fam) / len(qo_middles | chsh_middles), 4) if (qo_middles | chsh_middles) else 0
        }
    }
}

RESULTS.mkdir(parents=True, exist_ok=True)
with open(RESULTS / 'en_census.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'en_census.json'}")
