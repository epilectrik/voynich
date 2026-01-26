"""
Q2: AUXILIARY Feature Matrix

Build per-class distributional profiles for all 20 AX classes.
Features: position, REGIME, section, morphology, adjacency.
Output feeds clustering and transition analysis scripts.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scripts.voynich import Transcript, Morphology

# Paths
BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
REGIME_FILE = BASE / 'phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json'
CENSUS_FILE = BASE / 'phases/AUXILIARY_STRATIFICATION/results/ax_census.json'
RESULTS = BASE / 'phases/AUXILIARY_STRATIFICATION/results'

# Load data
tx = Transcript()
tokens = list(tx.currier_b())

with open(CLASS_MAP) as f:
    class_data = json.load(f)
token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}

with open(REGIME_FILE) as f:
    regime_data = json.load(f)
folio_regime = {}
for regime, folios in regime_data.items():
    for folio in folios:
        folio_regime[folio] = regime

with open(CENSUS_FILE) as f:
    census = json.load(f)
AX_CLASSES = set(census['definitive_ax_classes'])

morph = Morphology()

# Define section mapper
def get_section(folio):
    try:
        num = int(''.join(c for c in folio if c.isdigit())[:3])
    except:
        return 'UNKNOWN'
    if num <= 25:
        return 'HERBAL_A'
    elif num <= 56:
        return 'HERBAL_B'
    elif num <= 67:
        return 'PHARMA'
    elif num <= 73:
        return 'ASTRO'
    elif num <= 84:
        return 'BIO'
    elif num <= 86:
        return 'COSMO'
    elif num <= 102:
        return 'RECIPE_A'
    else:
        return 'RECIPE_B'

# Complete role map (ICC-based + C560 correction)
# CC: 10, 11, 12, 17 (C560)
# EN: 8, 31-37, 39, 41-49 (minus FL classes 38, 40)
# FL: 7, 30, 38, 40
# FQ: 9, 13, 23
ICC_CC = {10, 11, 12, 17}
ICC_EN = {8, 31, 32, 33, 34, 35, 36, 37, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49}
ICC_FL = {7, 30, 38, 40}
ICC_FQ = {9, 13, 23}

def get_role(cls):
    if cls in ICC_CC: return 'CC'
    if cls in ICC_EN: return 'EN'
    if cls in ICC_FL: return 'FL'
    if cls in ICC_FQ: return 'FQ'
    if cls in AX_CLASSES: return 'AX'
    return 'UN'

# ============================================================
# BUILD LINE STRUCTURES
# ============================================================
print("Building line structures...")

lines = defaultdict(list)
for token in tokens:
    word = token.word.replace('*', '').strip()
    if not word:
        continue
    cls = token_to_class.get(word)
    folio = token.folio
    line = token.line
    lines[(folio, line)].append({
        'word': word,
        'class': cls,
        'role': get_role(cls) if cls else 'UN',
        'folio': folio,
    })

# ============================================================
# COMPUTE FEATURES PER AX CLASS
# ============================================================
print("Computing per-class features...")

features = {}

for ax_cls in sorted(AX_CLASSES):
    # Collect all positions, contexts, etc.
    positions = []       # normalized 0-1
    initial_count = 0
    final_count = 0
    total_count = 0
    regime_counts = Counter()
    section_counts = Counter()
    left_role_counts = Counter()  # what role precedes this class
    right_role_counts = Counter()  # what role follows this class
    adj_energy = 0       # count of tokens adjacent to EN
    folio_set = set()

    # Morphological analysis of class members
    class_tokens = [tok for tok, cls in token_to_class.items() if cls == ax_cls]
    prefix_counts = Counter()
    suffix_counts = Counter()
    artic_count = 0
    for t in class_tokens:
        m = morph.extract(t)
        prefix_counts[m.prefix or 'NONE'] += 1
        suffix_counts[m.suffix or 'NONE'] += 1
        if m.has_articulator:
            artic_count += 1

    # Scan lines for positional and contextual features
    for (folio, line_id), line_tokens in lines.items():
        n = len(line_tokens)
        if n == 0:
            continue

        for i, tok in enumerate(line_tokens):
            if tok['class'] != ax_cls:
                continue

            total_count += 1
            folio_set.add(folio)

            # Position (normalized)
            pos = i / (n - 1) if n > 1 else 0.5
            positions.append(pos)

            # Initial/final
            if i == 0:
                initial_count += 1
            if i == n - 1:
                final_count += 1

            # REGIME
            regime = folio_regime.get(folio, 'UNKNOWN')
            regime_counts[regime] += 1

            # Section
            section = get_section(folio)
            section_counts[section] += 1

            # Left/right context (role of adjacent token)
            if i > 0:
                left_role_counts[line_tokens[i-1]['role']] += 1
            if i < n - 1:
                right_role_counts[line_tokens[i+1]['role']] += 1

            # Adjacent to ENERGY?
            if (i > 0 and line_tokens[i-1]['role'] == 'EN') or \
               (i < n - 1 and line_tokens[i+1]['role'] == 'EN'):
                adj_energy += 1

    if total_count == 0:
        continue

    # Compute derived features
    positions_arr = np.array(positions)
    mean_pos = float(np.mean(positions_arr))
    var_pos = float(np.var(positions_arr))
    initial_rate = initial_count / total_count
    final_rate = final_count / total_count

    # REGIME entropy
    regime_total = sum(regime_counts.values())
    if regime_total > 0:
        regime_probs = [c / regime_total for c in regime_counts.values() if c > 0]
        regime_entropy = -sum(p * np.log2(p) for p in regime_probs) / np.log2(4) if len(regime_probs) > 1 else 0
    else:
        regime_entropy = 0

    # REGIME shares
    regime_shares = {}
    for r in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        regime_shares[r] = regime_counts.get(r, 0) / regime_total if regime_total > 0 else 0

    # Section shares (for B sections)
    section_total = sum(section_counts.values())
    section_shares = {}
    for s in ['HERBAL_A', 'HERBAL_B', 'PHARMA', 'BIO', 'RECIPE_A', 'RECIPE_B', 'ASTRO', 'COSMO']:
        section_shares[s] = section_counts.get(s, 0) / section_total if section_total > 0 else 0

    # Morphology
    n_types = len(class_tokens)
    prefix_rate = 1.0 - (prefix_counts.get('NONE', 0) / n_types if n_types > 0 else 0)
    suffix_rate = 1.0 - (suffix_counts.get('NONE', 0) / n_types if n_types > 0 else 0)
    artic_rate = artic_count / n_types if n_types > 0 else 0
    dominant_prefix = max(prefix_counts, key=prefix_counts.get) if prefix_counts else 'NONE'

    # Energy adjacency rate
    energy_adj_rate = adj_energy / total_count

    # Left/right context shares
    left_total = sum(left_role_counts.values())
    right_total = sum(right_role_counts.values())
    left_en = left_role_counts.get('EN', 0) / left_total if left_total > 0 else 0
    right_en = right_role_counts.get('EN', 0) / right_total if right_total > 0 else 0
    left_ax = left_role_counts.get('AX', 0) / left_total if left_total > 0 else 0
    right_ax = right_role_counts.get('AX', 0) / right_total if right_total > 0 else 0

    features[ax_cls] = {
        'class': ax_cls,
        'n_types': n_types,
        'n_tokens': total_count,
        'n_folios': len(folio_set),
        # Position
        'mean_position': round(mean_pos, 4),
        'var_position': round(var_pos, 4),
        'initial_rate': round(initial_rate, 4),
        'final_rate': round(final_rate, 4),
        # REGIME
        'regime_entropy': round(regime_entropy, 4),
        'regime_shares': {k: round(v, 4) for k, v in regime_shares.items()},
        # Section
        'section_shares': {k: round(v, 4) for k, v in section_shares.items()},
        # Morphology
        'prefix_rate': round(prefix_rate, 4),
        'suffix_rate': round(suffix_rate, 4),
        'articulator_rate': round(artic_rate, 4),
        'dominant_prefix': dominant_prefix,
        # Adjacency
        'energy_adj_rate': round(energy_adj_rate, 4),
        'left_en_rate': round(left_en, 4),
        'right_en_rate': round(right_en, 4),
        'left_ax_rate': round(left_ax, 4),
        'right_ax_rate': round(right_ax, 4),
    }

# ============================================================
# DISPLAY RESULTS
# ============================================================
print("=" * 90)
print("Q2: AUXILIARY FEATURE MATRIX")
print("=" * 90)

# Positional profile
print("\n" + "-" * 90)
print("POSITIONAL PROFILES")
print("-" * 90)
print(f"{'Cls':>3} {'Tok':>5} {'MeanPos':>8} {'VarPos':>8} {'Init%':>7} {'Final%':>7} {'Bias'}")
for cls in sorted(features.keys()):
    f = features[cls]
    bias = 'INIT' if f['initial_rate'] > 0.20 else ('FINAL' if f['final_rate'] > 0.20 else 'MED')
    print(f"{cls:3d} {f['n_tokens']:5d} {f['mean_position']:8.3f} {f['var_position']:8.4f} "
          f"{f['initial_rate']*100:6.1f}% {f['final_rate']*100:6.1f}% {bias}")

# REGIME profile
print("\n" + "-" * 90)
print("REGIME PROFILES")
print("-" * 90)
print(f"{'Cls':>3} {'R1%':>6} {'R2%':>6} {'R3%':>6} {'R4%':>6} {'Entropy':>8} {'Specialist?'}")
for cls in sorted(features.keys()):
    f = features[cls]
    rs = f['regime_shares']
    max_r = max(rs, key=rs.get)
    max_val = rs[max_r]
    specialist = f'{max_r}' if max_val > 0.40 else '-'
    print(f"{cls:3d} {rs['REGIME_1']*100:5.1f} {rs['REGIME_2']*100:5.1f} "
          f"{rs['REGIME_3']*100:5.1f} {rs['REGIME_4']*100:5.1f} "
          f"{f['regime_entropy']:8.3f} {specialist}")

# Section profile
print("\n" + "-" * 90)
print("SECTION PROFILES (B sections only)")
print("-" * 90)
print(f"{'Cls':>3} {'HB%':>6} {'PH%':>6} {'BIO%':>6} {'RB%':>6} {'RA%':>6} {'Specialist?'}")
for cls in sorted(features.keys()):
    f = features[cls]
    ss = f['section_shares']
    # Major B sections
    hb = ss.get('HERBAL_B', 0)
    ph = ss.get('PHARMA', 0)
    bio = ss.get('BIO', 0)
    rb = ss.get('RECIPE_B', 0)
    ra = ss.get('RECIPE_A', 0)
    max_s = max([('HB', hb), ('PH', ph), ('BIO', bio), ('RB', rb), ('RA', ra)], key=lambda x: x[1])
    specialist = max_s[0] if max_s[1] > 0.40 else '-'
    print(f"{cls:3d} {hb*100:5.1f} {ph*100:5.1f} {bio*100:5.1f} {rb*100:5.1f} {ra*100:5.1f} {specialist}")

# Morphological profile
print("\n" + "-" * 90)
print("MORPHOLOGICAL PROFILES")
print("-" * 90)
print(f"{'Cls':>3} {'Types':>5} {'Prefix%':>8} {'Suffix%':>8} {'Artic%':>8} {'DomPrefix'}")
for cls in sorted(features.keys()):
    f = features[cls]
    print(f"{cls:3d} {f['n_types']:5d} {f['prefix_rate']*100:7.1f} {f['suffix_rate']*100:7.1f} "
          f"{f['articulator_rate']*100:7.1f} {f['dominant_prefix']}")

# Adjacency profile
print("\n" + "-" * 90)
print("ADJACENCY PROFILES")
print("-" * 90)
print(f"{'Cls':>3} {'EN_adj%':>8} {'L_EN%':>7} {'R_EN%':>7} {'L_AX%':>7} {'R_AX%':>7}")
for cls in sorted(features.keys()):
    f = features[cls]
    print(f"{cls:3d} {f['energy_adj_rate']*100:7.1f} {f['left_en_rate']*100:6.1f} "
          f"{f['right_en_rate']*100:6.1f} {f['left_ax_rate']*100:6.1f} "
          f"{f['right_ax_rate']*100:6.1f}")

# ============================================================
# SUMMARY STATISTICS
# ============================================================
print("\n" + "=" * 90)
print("SUMMARY")
print("=" * 90)

all_feats = list(features.values())
pos_arr = np.array([f['mean_position'] for f in all_feats])
init_arr = np.array([f['initial_rate'] for f in all_feats])
final_arr = np.array([f['final_rate'] for f in all_feats])
en_adj_arr = np.array([f['energy_adj_rate'] for f in all_feats])

print(f"\nPosition: mean={np.mean(pos_arr):.3f}, std={np.std(pos_arr):.3f}, "
      f"range=[{np.min(pos_arr):.3f}, {np.max(pos_arr):.3f}]")
print(f"Initial rate: mean={np.mean(init_arr):.3f}, max={np.max(init_arr):.3f} (class {all_feats[np.argmax(init_arr)]['class']})")
print(f"Final rate: mean={np.mean(final_arr):.3f}, max={np.max(final_arr):.3f} (class {all_feats[np.argmax(final_arr)]['class']})")
print(f"Energy adjacency: mean={np.mean(en_adj_arr):.3f}, range=[{np.min(en_adj_arr):.3f}, {np.max(en_adj_arr):.3f}]")

# Identify position extremes
init_classes = [f['class'] for f in all_feats if f['initial_rate'] > 0.20]
final_classes = [f['class'] for f in all_feats if f['final_rate'] > 0.20]
medial_classes = [f['class'] for f in all_feats if f['initial_rate'] <= 0.20 and f['final_rate'] <= 0.20]

print(f"\nPosition groups:")
print(f"  INITIAL-biased (>20% initial): {init_classes}")
print(f"  FINAL-biased (>20% final): {final_classes}")
print(f"  MEDIAL (neither): {medial_classes}")

# Save results
with open(RESULTS / 'ax_features.json', 'w') as f:
    json.dump(features, f, indent=2, default=str)

print(f"\nFeature matrix saved to {RESULTS / 'ax_features.json'}")
