"""
Script 4: Hazard Anatomy for FL and FQ

Deep hazard participation analysis. CC and AX have 0% hazard exposure (C541).
Analyzes: per-class hazard profiles, direction, gateway depth,
hazard neighborhoods, section-specific rates, non-hazard class avoidance.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scripts.voynich import Transcript, Morphology

BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
REGIME_FILE = BASE / 'phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json'
CENSUS = BASE / 'phases/SMALL_ROLE_ANATOMY/results/sr_census.json'
RESULTS = BASE / 'phases/SMALL_ROLE_ANATOMY/results'

# Load data
tx = Transcript()
morph = Morphology()
tokens = list(tx.currier_b())

with open(CLASS_MAP) as f:
    class_data = json.load(f)
token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}
ALL_CLASSES = set(token_to_class.values())

with open(REGIME_FILE) as f:
    regime_data = json.load(f)
folio_regime = {}
for regime, folios in regime_data.items():
    for folio in folios:
        folio_regime[folio] = regime

with open(CENSUS) as f:
    census = json.load(f)

# Role definitions from census
EN_FINAL = set(census['resolved_roles']['EN']['classes'])
FL_FINAL = set(census['resolved_roles']['FL']['classes'])
CC_FINAL = set(census['resolved_roles']['CC']['classes'])
FQ_FINAL = set(census['resolved_roles']['FQ']['classes'])
AX_FINAL = set(census['resolved_roles']['AX']['classes'])

def get_role(cls):
    if cls in CC_FINAL: return 'CC'
    if cls in FL_FINAL: return 'FL'
    if cls in FQ_FINAL: return 'FQ'
    if cls in EN_FINAL: return 'EN'
    if cls in AX_FINAL: return 'AX'
    return 'UN'

def get_section(folio):
    try:
        num = int(''.join(c for c in folio if c.isdigit())[:3])
    except Exception:
        return 'UNKNOWN'
    if num <= 56:
        return 'HERBAL'
    elif num <= 67:
        return 'PHARMA'
    elif num <= 84:
        return 'BIO'
    else:
        return 'RECIPE'

# ============================================================
# THE 17 FORBIDDEN TRANSITIONS (from C109)
# ============================================================
FORBIDDEN_TRANSITIONS = [
    ('shey', 'aiin'), ('shey', 'al'), ('shey', 'c'),
    ('dy', 'aiin'), ('dy', 'chey'), ('chey', 'chedy'), ('chey', 'shedy'),
    ('chedy', 'ee'), ('c', 'ee'), ('shedy', 'aiin'), ('shedy', 'o'),
    ('chol', 'r'), ('l', 'chol'), ('or', 'dal'),
    ('he', 'or'), ('ar', 'dal'), ('he', 't'),
]

HAZARD_CLASS = {
    ('shey', 'aiin'): 'PHASE_ORDERING', ('shey', 'al'): 'PHASE_ORDERING',
    ('shey', 'c'): 'PHASE_ORDERING', ('dy', 'aiin'): 'PHASE_ORDERING',
    ('dy', 'chey'): 'PHASE_ORDERING', ('chey', 'chedy'): 'PHASE_ORDERING',
    ('chey', 'shedy'): 'PHASE_ORDERING',
    ('chedy', 'ee'): 'COMPOSITION_JUMP', ('c', 'ee'): 'COMPOSITION_JUMP',
    ('shedy', 'aiin'): 'COMPOSITION_JUMP', ('shedy', 'o'): 'COMPOSITION_JUMP',
    ('chol', 'r'): 'CONTAINMENT_TIMING', ('l', 'chol'): 'CONTAINMENT_TIMING',
    ('or', 'dal'): 'CONTAINMENT_TIMING', ('he', 'or'): 'CONTAINMENT_TIMING',
    ('ar', 'dal'): 'RATE_MISMATCH',
    ('he', 't'): 'ENERGY_OVERSHOOT',
}

# Build bidirectional forbidden set
forbidden_set = set()
for a, b in FORBIDDEN_TRANSITIONS:
    forbidden_set.add((a, b))
    forbidden_set.add((b, a))

# Hazard-involved tokens
hazard_tokens = set()
for a, b in FORBIDDEN_TRANSITIONS:
    hazard_tokens.add(a)
    hazard_tokens.add(b)

# Map tokens to hazard involvement info
token_hazard_types = defaultdict(set)  # token -> set of hazard class names
token_hazard_direction = defaultdict(lambda: {'source': 0, 'target': 0})
for a, b in FORBIDDEN_TRANSITIONS:
    hclass = HAZARD_CLASS[(a, b)]
    token_hazard_types[a].add(hclass)
    token_hazard_types[b].add(hclass)
    token_hazard_direction[a]['source'] += 1
    token_hazard_direction[b]['target'] += 1

print("=" * 70)
print("HAZARD ANATOMY: FL AND FQ")
print("=" * 70)

# ============================================================
# 1. TOKEN-LEVEL HAZARD MAPPING
# ============================================================
print("\n" + "-" * 70)
print("1. TOKEN-LEVEL HAZARD MAPPING")
print("-" * 70)

# Which FL/FQ tokens are in the forbidden transitions?
print("\nHazard tokens in corpus vocabulary:")
for tok in sorted(hazard_tokens):
    cls = token_to_class.get(tok)
    if cls is not None:
        role = get_role(cls)
        htypes = sorted(token_hazard_types[tok])
        direction = token_hazard_direction[tok]
        print(f"  {tok:>8}: Class {cls} ({role}), hazards: {htypes}, "
              f"source={direction['source']}, target={direction['target']}")
    else:
        print(f"  {tok:>8}: NOT IN VOCABULARY")

# ============================================================
# 2. PER-CLASS HAZARD PROFILES
# ============================================================
print("\n" + "-" * 70)
print("2. PER-CLASS HAZARD PROFILES (FL + FQ)")
print("-" * 70)

# Hazard classes per instruction class
class_hazard_involvement = defaultdict(lambda: {'types': set(), 'tokens': set(), 'total_transitions': 0})

for a, b in FORBIDDEN_TRANSITIONS:
    hclass = HAZARD_CLASS[(a, b)]
    for tok in [a, b]:
        cls = token_to_class.get(tok)
        if cls is not None:
            class_hazard_involvement[cls]['types'].add(hclass)
            class_hazard_involvement[cls]['tokens'].add(tok)
            class_hazard_involvement[cls]['total_transitions'] += 1

target_roles = {'FL': FL_FINAL, 'FQ': FQ_FINAL}
for role_name, role_classes in target_roles.items():
    print(f"\n{role_name}:")
    for cls in sorted(role_classes):
        info = class_hazard_involvement.get(cls, {'types': set(), 'tokens': set(), 'total_transitions': 0})
        if info['types']:
            print(f"  Class {cls}: HAZARD-INVOLVED")
            print(f"    Hazard types: {sorted(info['types'])}")
            print(f"    Hazard tokens: {sorted(info['tokens'])}")
            print(f"    Transition count: {info['total_transitions']}")
        else:
            print(f"  Class {cls}: NON-HAZARDOUS (zero involvement)")

# ============================================================
# 3. CORPUS HAZARD OCCURRENCES
# ============================================================
print("\n" + "-" * 70)
print("3. CORPUS HAZARD OCCURRENCES (adjacent forbidden pairs)")
print("-" * 70)

# Build line-grouped tokens
lines = defaultdict(list)
for token in tokens:
    word = token.word.replace('*', '').strip()
    if not word:
        continue
    lines[(token.folio, token.line)].append({
        'word': word,
        'folio': token.folio,
        'class': token_to_class.get(word),
    })

# Scan for actual forbidden transitions in corpus
hazard_events = []  # list of (folio, line, pos, token_a, token_b, hazard_class)
for (folio, line_id), line_tokens in lines.items():
    for i in range(len(line_tokens) - 1):
        a = line_tokens[i]['word']
        b = line_tokens[i+1]['word']
        if (a, b) in forbidden_set:
            hclass = HAZARD_CLASS.get((a, b)) or HAZARD_CLASS.get((b, a), 'UNKNOWN')
            cls_a = line_tokens[i]['class']
            cls_b = line_tokens[i+1]['class']
            hazard_events.append({
                'folio': folio,
                'line': line_id,
                'pos': i,
                'token_a': a,
                'token_b': b,
                'class_a': cls_a,
                'class_b': cls_b,
                'role_a': get_role(cls_a) if cls_a else 'UN',
                'role_b': get_role(cls_b) if cls_b else 'UN',
                'hazard_class': hclass,
                'section': get_section(folio),
            })

print(f"\nTotal forbidden transitions in corpus: {len(hazard_events)}")

# Count by hazard class
hclass_counts = Counter(e['hazard_class'] for e in hazard_events)
print(f"\nBy hazard class:")
for hc, cnt in hclass_counts.most_common():
    print(f"  {hc}: {cnt}")

# Count by role involvement
role_involvement = Counter()
for e in hazard_events:
    role_involvement[e['role_a']] += 1
    role_involvement[e['role_b']] += 1
print(f"\nRole involvement in forbidden transitions:")
for role, cnt in role_involvement.most_common():
    print(f"  {role}: {cnt}")

# Count by class
class_involvement_corpus = Counter()
for e in hazard_events:
    if e['class_a'] is not None:
        class_involvement_corpus[e['class_a']] += 1
    if e['class_b'] is not None:
        class_involvement_corpus[e['class_b']] += 1
print(f"\nClass involvement (top 10):")
for cls, cnt in class_involvement_corpus.most_common(10):
    print(f"  Class {cls} ({get_role(cls)}): {cnt}")

# ============================================================
# 4. HAZARD DIRECTION (source vs target)
# ============================================================
print("\n" + "-" * 70)
print("4. HAZARD DIRECTION (which role initiates vs receives)")
print("-" * 70)

source_counts = Counter()
target_counts = Counter()
for e in hazard_events:
    source_counts[e['role_a']] += 1
    target_counts[e['role_b']] += 1

print(f"\n{'Role':>6} {'As source':>10} {'As target':>10} {'Ratio':>8}")
all_dir_roles = set(source_counts.keys()) | set(target_counts.keys())
for role in sorted(all_dir_roles):
    src = source_counts[role]
    tgt = target_counts[role]
    ratio = src / tgt if tgt > 0 else float('inf')
    print(f"{role:>6} {src:>10} {tgt:>10} {ratio:>7.2f}")

# ============================================================
# 5. HAZARD NEIGHBORHOOD (+-3 tokens)
# ============================================================
print("\n" + "-" * 70)
print("5. HAZARD NEIGHBORHOOD (roles in +-3 window)")
print("-" * 70)

neighborhood_roles = Counter()
for e in hazard_events:
    folio = e['folio']
    line_id = e['line']
    pos = e['pos']
    line_toks = lines[(folio, line_id)]

    for offset in range(-3, 4):
        if offset == 0 or offset == 1:
            continue  # skip the pair itself
        idx = pos + offset
        if 0 <= idx < len(line_toks):
            cls = line_toks[idx]['class']
            if cls is not None:
                neighborhood_roles[get_role(cls)] += 1

total_neighborhood = sum(neighborhood_roles.values())
print(f"\nRoles in +-3 window of forbidden transitions ({total_neighborhood} observations):")
for role, cnt in neighborhood_roles.most_common():
    pct = cnt / total_neighborhood * 100
    print(f"  {role}: {cnt} ({pct:.1f}%)")

# Neighborhood classes
neighborhood_classes = Counter()
for e in hazard_events:
    folio = e['folio']
    line_id = e['line']
    pos = e['pos']
    line_toks = lines[(folio, line_id)]
    for offset in range(-3, 4):
        if offset == 0 or offset == 1:
            continue
        idx = pos + offset
        if 0 <= idx < len(line_toks):
            cls = line_toks[idx]['class']
            if cls is not None:
                neighborhood_classes[cls] += 1

print(f"\nClasses in hazard neighborhoods (top 15):")
for cls, cnt in neighborhood_classes.most_common(15):
    print(f"  Class {cls} ({get_role(cls)}): {cnt}")

# ============================================================
# 6. SECTION-SPECIFIC HAZARD RATES
# ============================================================
print("\n" + "-" * 70)
print("6. SECTION-SPECIFIC HAZARD RATES")
print("-" * 70)

section_hazards = Counter(e['section'] for e in hazard_events)
section_totals = Counter()
for (folio, _), line_toks in lines.items():
    sec = get_section(folio)
    section_totals[sec] += len(line_toks)

SECTIONS = ['HERBAL', 'PHARMA', 'BIO', 'RECIPE']
print(f"\n{'Section':>8} {'Hazards':>8} {'Tokens':>8} {'Rate':>8}")
for sec in SECTIONS:
    h = section_hazards.get(sec, 0)
    t = section_totals.get(sec, 0)
    rate = h / t * 1000 if t > 0 else 0  # per 1000 tokens
    print(f"{sec:>8} {h:>8} {t:>8} {rate:>7.2f} per 1000")

# Which FL/FQ classes contribute to hazards by section?
for sec in SECTIONS:
    sec_events = [e for e in hazard_events if e['section'] == sec]
    if not sec_events:
        continue
    sec_classes = Counter()
    for e in sec_events:
        for cls in [e['class_a'], e['class_b']]:
            if cls and get_role(cls) in ('FL', 'FQ'):
                sec_classes[cls] += 1
    if sec_classes:
        top = sec_classes.most_common(3)
        top_str = ', '.join(f"Class {c}({cnt})" for c, cnt in top)
        print(f"  {sec}: FL/FQ contributors: {top_str}")

# ============================================================
# 7. NON-HAZARD CLASS BEHAVIOR
# ============================================================
print("\n" + "-" * 70)
print("7. NON-HAZARD FL/FQ CLASSES: HAZARD AVOIDANCE")
print("-" * 70)

# FL hazard: {7, 30}. Non-hazard: {38, 40}
# FQ hazard: {9, 23}. Non-hazard: {13, 14}
# Compute average distance to nearest hazard event for each class

# Pre-compute hazard positions per line
hazard_positions = defaultdict(set)  # (folio, line) -> set of positions
for e in hazard_events:
    hazard_positions[(e['folio'], e['line'])].add(e['pos'])
    hazard_positions[(e['folio'], e['line'])].add(e['pos'] + 1)

class_hazard_distances = defaultdict(list)
for (folio, line_id), line_toks in lines.items():
    haz_pos = hazard_positions.get((folio, line_id), set())
    if not haz_pos:
        continue

    for i, tok in enumerate(line_toks):
        cls = tok['class']
        if cls is None:
            continue
        if get_role(cls) not in ('FL', 'FQ'):
            continue
        # Distance to nearest hazard position
        min_dist = min(abs(i - hp) for hp in haz_pos)
        class_hazard_distances[cls].append(min_dist)

print(f"\nAverage distance to nearest hazard (in lines containing hazards):")
print(f"{'Class':>6} {'Role':>5} {'Hazard?':>8} {'N':>6} {'MeanDist':>9} {'MedianDist':>11}")
for cls in sorted(class_hazard_distances.keys()):
    dists = class_hazard_distances[cls]
    role = get_role(cls)
    is_haz = cls in {7, 30, 9, 23}
    print(f"{cls:>6} {role:>5} {'YES' if is_haz else 'no':>8} {len(dists):>6} "
          f"{np.mean(dists):>9.2f} {np.median(dists):>11.1f}")

# ============================================================
# 8. HAZARD CLASS vs NON-HAZARD CLASS COMPARISON
# ============================================================
print("\n" + "-" * 70)
print("8. HAZARD vs NON-HAZARD CLASS COMPARISON (FL, FQ)")
print("-" * 70)

# Use feature data if available
features_file = RESULTS / 'sr_features.json'
if features_file.exists():
    with open(features_file) as f:
        feat_data = json.load(f)

    for role_name, role_classes, haz_classes in [
        ('FL', FL_FINAL, {7, 30}),
        ('FQ', FQ_FINAL, {9, 23})
    ]:
        non_haz = role_classes - haz_classes
        print(f"\n{role_name}:")
        print(f"  Hazard classes: {sorted(haz_classes)}")
        print(f"  Non-hazard classes: {sorted(non_haz)}")

        for cls in sorted(role_classes):
            f = feat_data.get(str(cls))
            if not f or f.get('n_tokens', 0) == 0:
                print(f"    Class {cls}: no data")
                continue
            haz_label = 'HAZ' if cls in haz_classes else 'safe'
            print(f"    Class {cls} [{haz_label}]: pos={f['mean_position']:.3f}, "
                  f"init={f['initial_rate']*100:.1f}%, final={f['final_rate']*100:.1f}%, "
                  f"self_chain={f['self_chain_rate']*100:.1f}%, tokens={f['n_tokens']}")
else:
    print("  (feature data not available; run sr_feature_matrix.py first)")

# ============================================================
# SAVE RESULTS
# ============================================================

results = {
    'total_corpus_hazards': len(hazard_events),
    'hazard_class_counts': dict(hclass_counts),
    'role_involvement': dict(role_involvement),
    'class_involvement': {str(k): v for k, v in class_involvement_corpus.most_common()},
    'direction': {
        'source': dict(source_counts),
        'target': dict(target_counts),
    },
    'neighborhood_roles': dict(neighborhood_roles),
    'section_hazard_rates': {
        sec: {
            'hazards': section_hazards.get(sec, 0),
            'tokens': section_totals.get(sec, 0),
            'rate_per_1000': round(section_hazards.get(sec, 0) / section_totals.get(sec, 1) * 1000, 3)
        }
        for sec in SECTIONS
    },
    'class_hazard_distances': {
        str(cls): {
            'n': len(dists),
            'mean': round(np.mean(dists), 3),
            'median': float(np.median(dists)),
            'is_hazard_class': cls in {7, 30, 9, 23},
            'role': get_role(cls)
        }
        for cls, dists in class_hazard_distances.items()
    },
    'per_class_hazard_profiles': {
        str(cls): {
            'hazard_types': sorted(info['types']),
            'hazard_tokens': sorted(info['tokens']),
            'transition_count': info['total_transitions'],
            'role': get_role(cls),
            'is_fl_or_fq': cls in FL_FINAL or cls in FQ_FINAL
        }
        for cls, info in class_hazard_involvement.items()
    },
    'hazard_events_sample': hazard_events[:20],
}

RESULTS.mkdir(parents=True, exist_ok=True)
with open(RESULTS / 'sr_hazard_anatomy.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults saved to {RESULTS / 'sr_hazard_anatomy.json'}")
