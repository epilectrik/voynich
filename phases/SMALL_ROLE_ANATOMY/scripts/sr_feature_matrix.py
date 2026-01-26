"""
Script 2: Small Role Feature Matrix

Build per-class distributional profiles for all CC, FL, FQ classes.
Features: position, REGIME, section, morphology, adjacency.
Same structure as en_feature_matrix.py for cross-role comparability.
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

# Role definitions (ICC-based, anchored on EN C573 and FL consensus)
EN_FINAL = ({8} | set(range(31, 50)) - {7, 30, 38, 40}) & ALL_CLASSES
FL_FINAL = {7, 30, 38, 40}
CC_FINAL = {10, 11, 12}
FQ_FINAL = {9, 13, 14, 23}
AX_FINAL = ALL_CLASSES - EN_FINAL - FL_FINAL - CC_FINAL - FQ_FINAL

# Target classes for this script
TARGET_CLASSES = CC_FINAL | FL_FINAL | FQ_FINAL

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
    lines[(token.folio, token.line)].append({
        'word': word,
        'class': cls,
        'role': get_role(cls) if cls else 'UN',
        'folio': token.folio,
    })

# Invert: class -> token types
class_to_tokens = defaultdict(list)
for tok, cls in token_to_class.items():
    class_to_tokens[cls].append(tok)

# ============================================================
# COMPUTE FEATURES PER CLASS
# ============================================================
print("Computing per-class features for CC, FL, FQ...")

features = {}

for target_cls in sorted(TARGET_CLASSES):
    positions = []
    initial_count = 0
    final_count = 0
    total_count = 0
    regime_counts = Counter()
    section_counts = Counter()
    left_role_counts = Counter()
    right_role_counts = Counter()
    self_chain_count = 0
    role_chain_count = 0
    folio_set = set()

    # Morphological analysis of class members (types)
    class_tokens_list = class_to_tokens.get(target_cls, [])
    prefix_counts = Counter()
    suffix_counts = Counter()
    middle_counts = Counter()
    artic_count = 0
    for t in class_tokens_list:
        m = morph.extract(t)
        prefix_counts[m.prefix or 'NONE'] += 1
        suffix_counts[m.suffix or 'NONE'] += 1
        middle_counts[m.middle or 'NONE'] += 1
        if m.has_articulator:
            artic_count += 1

    # Scan lines for positional and contextual features
    role = get_role(target_cls)
    for (folio, line_id), line_tokens in lines.items():
        n = len(line_tokens)
        if n == 0:
            continue

        for i, tok in enumerate(line_tokens):
            if tok['class'] != target_cls:
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
            reg = folio_regime.get(folio, 'UNKNOWN')
            regime_counts[reg] += 1

            # Section
            section = get_section(folio)
            section_counts[section] += 1

            # Left/right context (role)
            if i > 0:
                left_role_counts[line_tokens[i-1]['role']] += 1
                if line_tokens[i-1]['class'] == target_cls:
                    self_chain_count += 1
                if line_tokens[i-1]['role'] == role:
                    role_chain_count += 1
            if i < n - 1:
                right_role_counts[line_tokens[i+1]['role']] += 1

    if total_count == 0:
        # Class exists but has no corpus tokens (e.g., Class 12 = k)
        features[target_cls] = {
            'class': target_cls,
            'role': role,
            'n_types': len(class_tokens_list),
            'n_tokens': 0,
            'n_folios': 0,
            'NOTE': 'Zero corpus tokens (class defined but not instantiated)'
        }
        continue

    # Derived features
    positions_arr = np.array(positions)
    mean_pos = float(np.mean(positions_arr))
    var_pos = float(np.var(positions_arr))
    initial_rate = initial_count / total_count
    final_rate = final_count / total_count

    # REGIME entropy (normalized to [0,1] via log2(4))
    regime_total = sum(regime_counts.values())
    if regime_total > 0:
        regime_probs = [c / regime_total for c in regime_counts.values() if c > 0]
        regime_entropy = -sum(p * np.log2(p) for p in regime_probs) / np.log2(4) if len(regime_probs) > 1 else 0
    else:
        regime_entropy = 0

    regime_shares = {}
    for r in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        regime_shares[r] = regime_counts.get(r, 0) / regime_total if regime_total > 0 else 0

    # Section shares
    section_total = sum(section_counts.values())
    section_shares = {}
    for s in ['HERBAL_A', 'HERBAL_B', 'PHARMA', 'BIO', 'RECIPE_A', 'RECIPE_B', 'ASTRO', 'COSMO']:
        section_shares[s] = section_counts.get(s, 0) / section_total if section_total > 0 else 0

    # Morphology
    n_types = len(class_tokens_list)
    prefix_rate = 1.0 - (prefix_counts.get('NONE', 0) / n_types if n_types > 0 else 0)
    suffix_rate = 1.0 - (suffix_counts.get('NONE', 0) / n_types if n_types > 0 else 0)
    artic_rate = artic_count / n_types if n_types > 0 else 0
    dominant_prefix = max(prefix_counts, key=prefix_counts.get) if prefix_counts else 'NONE'
    n_unique_middles = len([k for k in middle_counts if k != 'NONE'])
    mean_token_length = np.mean([len(t) for t in class_tokens_list]) if class_tokens_list else 0

    # Adjacency
    self_chain_rate = self_chain_count / total_count
    role_chain_rate = role_chain_count / total_count

    left_total = sum(left_role_counts.values())
    right_total = sum(right_role_counts.values())
    context_shares = {}
    for r_name in ['EN', 'AX', 'CC', 'FL', 'FQ', 'UN']:
        context_shares[f'left_{r_name}'] = left_role_counts.get(r_name, 0) / left_total if left_total > 0 else 0
        context_shares[f'right_{r_name}'] = right_role_counts.get(r_name, 0) / right_total if right_total > 0 else 0

    features[target_cls] = {
        'class': target_cls,
        'role': role,
        'n_types': n_types,
        'n_tokens': total_count,
        'n_folios': len(folio_set),
        'n_unique_middles': n_unique_middles,
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
        'mean_token_length': round(float(mean_token_length), 2),
        # Adjacency
        'self_chain_rate': round(self_chain_rate, 4),
        'role_chain_rate': round(role_chain_rate, 4),
        'context_shares': {k: round(v, 4) for k, v in context_shares.items()},
    }

# ============================================================
# DISPLAY RESULTS
# ============================================================
print("=" * 90)
print("SMALL ROLE FEATURE MATRIX")
print("=" * 90)

# Positional profile
for role_name in ['CC', 'FL', 'FQ']:
    role_classes = [c for c in sorted(features.keys()) if features[c].get('role') == role_name]
    print(f"\n--- {role_name} POSITIONAL PROFILES ---")
    print(f"{'Cls':>3} {'Tok':>5} {'Fol':>3} {'MeanPos':>8} {'VarPos':>8} {'Init%':>7} {'Final%':>7} {'Bias'}")
    for cls in role_classes:
        f = features[cls]
        if f['n_tokens'] == 0:
            print(f"{cls:3d}     0   0     --       --      --      -- EMPTY")
            continue
        bias = 'INIT' if f['initial_rate'] > 0.15 else ('FINAL' if f['final_rate'] > 0.15 else 'MED')
        print(f"{cls:3d} {f['n_tokens']:5d} {f['n_folios']:3d} {f['mean_position']:8.3f} {f['var_position']:8.4f} "
              f"{f['initial_rate']*100:6.1f}% {f['final_rate']*100:6.1f}% {bias}")

# REGIME profile
print(f"\n--- ALL SMALL ROLES: REGIME PROFILES ---")
print(f"{'Cls':>3} {'Role':>4} {'R1%':>6} {'R2%':>6} {'R3%':>6} {'R4%':>6} {'Entropy':>8}")
for cls in sorted(features.keys()):
    f = features[cls]
    if f['n_tokens'] == 0:
        continue
    rs = f['regime_shares']
    print(f"{cls:3d} {f['role']:>4} {rs['REGIME_1']*100:5.1f} {rs['REGIME_2']*100:5.1f} "
          f"{rs['REGIME_3']*100:5.1f} {rs['REGIME_4']*100:5.1f} "
          f"{f['regime_entropy']:8.3f}")

# Section profile
print(f"\n--- ALL SMALL ROLES: SECTION PROFILES ---")
print(f"{'Cls':>3} {'Role':>4} {'HB%':>6} {'PH%':>6} {'BIO%':>6} {'RA%':>6} {'RB%':>6}")
for cls in sorted(features.keys()):
    f = features[cls]
    if f['n_tokens'] == 0:
        continue
    ss = f['section_shares']
    print(f"{cls:3d} {f['role']:>4} {ss.get('HERBAL_B',0)*100:5.1f} {ss.get('PHARMA',0)*100:5.1f} "
          f"{ss.get('BIO',0)*100:5.1f} {ss.get('RECIPE_A',0)*100:5.1f} {ss.get('RECIPE_B',0)*100:5.1f}")

# Morphological profile
print(f"\n--- ALL SMALL ROLES: MORPHOLOGICAL PROFILES ---")
print(f"{'Cls':>3} {'Role':>4} {'Types':>5} {'MIDs':>5} {'Pfx%':>7} {'Sfx%':>7} {'Art%':>7} {'AvgLen':>6} {'DomPfx'}")
for cls in sorted(features.keys()):
    f = features[cls]
    if f['n_tokens'] == 0:
        print(f"{cls:3d} {f['role']:>4} {f['n_types']:5d}    --      --      --      --    -- EMPTY")
        continue
    print(f"{cls:3d} {f['role']:>4} {f['n_types']:5d} {f['n_unique_middles']:5d} {f['prefix_rate']*100:6.1f} "
          f"{f['suffix_rate']*100:6.1f} {f['articulator_rate']*100:6.1f} {f['mean_token_length']:5.1f}  {f['dominant_prefix']}")

# Adjacency profile
print(f"\n--- ALL SMALL ROLES: ADJACENCY PROFILES ---")
print(f"{'Cls':>3} {'Role':>4} {'Self%':>7} {'Same%':>7} {'L_EN%':>7} {'R_EN%':>7} {'L_AX%':>7} {'R_AX%':>7}")
for cls in sorted(features.keys()):
    f = features[cls]
    if f['n_tokens'] == 0:
        continue
    cs = f['context_shares']
    print(f"{cls:3d} {f['role']:>4} {f['self_chain_rate']*100:6.1f} {f['role_chain_rate']*100:6.1f} "
          f"{cs['left_EN']*100:6.1f} {cs['right_EN']*100:6.1f} "
          f"{cs['left_AX']*100:6.1f} {cs['right_AX']*100:6.1f}")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 90)
print("SUMMARY")
print("=" * 90)

active_feats = [f for f in features.values() if f['n_tokens'] > 0]

for role_name in ['CC', 'FL', 'FQ']:
    rfeats = [f for f in active_feats if f['role'] == role_name]
    if not rfeats:
        print(f"\n{role_name}: No active classes")
        continue
    tok_arr = np.array([f['n_tokens'] for f in rfeats])
    pos_arr = np.array([f['mean_position'] for f in rfeats])
    init_arr = np.array([f['initial_rate'] for f in rfeats])
    final_arr = np.array([f['final_rate'] for f in rfeats])

    print(f"\n{role_name} ({len(rfeats)} active classes):")
    print(f"  Token range: {int(tok_arr.min())} - {int(tok_arr.max())} (total {int(tok_arr.sum())})")
    print(f"  Position: mean={np.mean(pos_arr):.3f}, range=[{np.min(pos_arr):.3f}, {np.max(pos_arr):.3f}]")
    print(f"  Initial: mean={np.mean(init_arr)*100:.1f}%, max={np.max(init_arr)*100:.1f}%")
    print(f"  Final:   mean={np.mean(final_arr)*100:.1f}%, max={np.max(final_arr)*100:.1f}%")

# Save
RESULTS.mkdir(parents=True, exist_ok=True)
with open(RESULTS / 'sr_features.json', 'w') as f:
    json.dump(features, f, indent=2, default=str)

print(f"\nFeature matrix saved to {RESULTS / 'sr_features.json'}")
