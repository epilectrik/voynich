"""
01_procedural_features.py - Extract procedural/temporal features per folio

Features:
- Tier densities (prep, thermo, extended)
- Positional means per tier
- Diversity and ratio metrics
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

print("="*70)
print("PROCEDURAL FEATURE EXTRACTION")
print("="*70)

# Three-tier MIDDLE definitions (from F-BRU-011/012/013)
PREP_MIDDLES = {'te', 'pch', 'lch', 'tch', 'ksh'}
THERMO_MIDDLES = {'k', 't', 'e'}  # Base forms only
EXTENDED_MIDDLES = {'ke', 'kch'}

# For detecting compound MIDDLEs
ALL_TIER_MIDDLES = PREP_MIDDLES | THERMO_MIDDLES | EXTENDED_MIDDLES

def classify_middle(middle):
    """Classify a MIDDLE into tier, handling compounds"""
    if not middle:
        return None

    # Check extended first (ke, kch are specific)
    for ext in EXTENDED_MIDDLES:
        if middle == ext or middle.startswith(ext) or ext in middle:
            return 'EXTENDED'

    # Check prep (multi-char, more specific)
    for prep in PREP_MIDDLES:
        if middle == prep or middle.startswith(prep) or prep in middle:
            return 'PREP'

    # Check thermo (single char base forms)
    for thermo in THERMO_MIDDLES:
        if middle == thermo:
            return 'THERMO'
        # Also check if it's a base form at start (e.g., 'ked' starts with 'k')
        if len(thermo) == 1 and middle.startswith(thermo) and middle not in EXTENDED_MIDDLES:
            # But not if it's ke or kch
            if not any(middle.startswith(ext) for ext in EXTENDED_MIDDLES):
                return 'THERMO'

    return None

def get_kernel_order_compliance(tokens_on_line):
    """Check if e, h, k appear in correct order on a line"""
    positions = {'e': [], 'h': [], 'k': []}

    for pos, tok in enumerate(tokens_on_line):
        m = morph.extract(tok['word'])
        if m and m.middle:
            for kernel in ['e', 'h', 'k']:
                if kernel in m.middle:
                    positions[kernel].append(pos)

    # Check ordering: mean(e) < mean(h) < mean(k)
    means = {}
    for kernel in ['e', 'h', 'k']:
        if positions[kernel]:
            means[kernel] = np.mean(positions[kernel])

    if len(means) < 2:
        return None  # Not enough kernels to check

    # Check e < h, h < k, e < k
    correct = 0
    total = 0

    if 'e' in means and 'h' in means:
        total += 1
        if means['e'] < means['h']:
            correct += 1

    if 'h' in means and 'k' in means:
        total += 1
        if means['h'] < means['k']:
            correct += 1

    if 'e' in means and 'k' in means:
        total += 1
        if means['e'] < means['k']:
            correct += 1

    return correct / total if total > 0 else None

# ============================================================
# EXTRACT FEATURES PER FOLIO
# ============================================================
print("\n--- Extracting Features Per Folio ---")

# Build per-folio, per-line token data
folio_lines = defaultdict(lambda: defaultdict(list))

for t in tx.currier_b():
    m = morph.extract(t.word)
    if not m:
        continue

    folio_lines[t.folio][t.line].append({
        'word': t.word,
        'middle': m.middle,
        'prefix': m.prefix,
        'position': t.position if hasattr(t, 'position') else None
    })

# Compute features per folio
folio_features = {}

for folio in sorted(folio_lines.keys()):
    lines = folio_lines[folio]

    # Flatten all tokens
    all_tokens = []
    for line_num in sorted(lines.keys()):
        line_tokens = lines[line_num]
        total_on_line = len(line_tokens)
        for i, tok in enumerate(line_tokens):
            tok['line_position'] = i / total_on_line if total_on_line > 1 else 0.5
            tok['line_num'] = line_num
            all_tokens.append(tok)

    total_tokens = len(all_tokens)
    if total_tokens < 20:  # Skip sparse folios
        continue

    # Tier counts and positions
    tier_counts = {'PREP': 0, 'THERMO': 0, 'EXTENDED': 0}
    tier_positions = {'PREP': [], 'THERMO': [], 'EXTENDED': []}

    # Prefix tracking for qo/chsh ratio
    qo_early = 0
    chsh_early = 0

    # Prep MIDDLE diversity
    prep_middles_used = set()

    # ke vs kch
    ke_count = 0
    kch_count = 0

    # Compute folio position (normalized line number)
    total_lines = len(lines)
    line_to_folio_pos = {ln: (i / total_lines) for i, ln in enumerate(sorted(lines.keys()))}

    for tok in all_tokens:
        middle = tok['middle']
        if not middle:
            continue

        tier = classify_middle(middle)
        if tier:
            tier_counts[tier] += 1
            folio_pos = line_to_folio_pos.get(tok['line_num'], 0.5)
            tier_positions[tier].append(folio_pos)

            if tier == 'PREP':
                for pm in PREP_MIDDLES:
                    if pm in middle:
                        prep_middles_used.add(pm)

            if tier == 'EXTENDED':
                if 'ke' in middle and 'kch' not in middle:
                    ke_count += 1
                elif 'kch' in middle:
                    kch_count += 1

        # QO vs CHSH in early lines (first 33%)
        if line_to_folio_pos.get(tok['line_num'], 1) < 0.33:
            prefix = tok['prefix']
            if prefix == 'qo':
                qo_early += 1
            elif prefix in {'ch', 'sh'}:
                chsh_early += 1

    # Compute kernel order compliance
    compliance_scores = []
    for line_num, line_tokens in lines.items():
        score = get_kernel_order_compliance(line_tokens)
        if score is not None:
            compliance_scores.append(score)

    # Compute features
    features = {
        'folio': folio,
        'total_tokens': total_tokens,

        # Tier densities
        'prep_density': tier_counts['PREP'] / total_tokens,
        'thermo_density': tier_counts['THERMO'] / total_tokens,
        'extended_density': tier_counts['EXTENDED'] / total_tokens,

        # Tier counts (raw)
        'prep_count': tier_counts['PREP'],
        'thermo_count': tier_counts['THERMO'],
        'extended_count': tier_counts['EXTENDED'],

        # Ratios
        'prep_thermo_ratio': (tier_counts['PREP'] / tier_counts['THERMO']) if tier_counts['THERMO'] > 0 else 0,
        'ke_kch_ratio': (ke_count / (ke_count + kch_count)) if (ke_count + kch_count) > 0 else 0.5,

        # Positional means
        'prep_mean_position': np.mean(tier_positions['PREP']) if tier_positions['PREP'] else 0.5,
        'thermo_mean_position': np.mean(tier_positions['THERMO']) if tier_positions['THERMO'] else 0.5,
        'extended_mean_position': np.mean(tier_positions['EXTENDED']) if tier_positions['EXTENDED'] else 0.5,

        # Tier spread (temporal separation)
        'tier_spread': (
            (np.mean(tier_positions['EXTENDED']) if tier_positions['EXTENDED'] else 0.5) -
            (np.mean(tier_positions['PREP']) if tier_positions['PREP'] else 0.5)
        ),

        # Diversity
        'prep_diversity': len(prep_middles_used) / 5,  # 5 possible prep MIDDLEs

        # QO/CHSH early ratio
        'qo_chsh_early_ratio': (qo_early / (qo_early + chsh_early)) if (qo_early + chsh_early) > 0 else 0.5,

        # Kernel order compliance
        'kernel_order_compliance': np.mean(compliance_scores) if compliance_scores else 0.5
    }

    folio_features[folio] = features

print(f"Features extracted for {len(folio_features)} folios")

# ============================================================
# SUMMARY STATISTICS
# ============================================================
print("\n--- Feature Summary Statistics ---")

feature_names = [
    'prep_density', 'thermo_density', 'extended_density',
    'prep_thermo_ratio', 'ke_kch_ratio',
    'prep_mean_position', 'thermo_mean_position', 'extended_mean_position',
    'tier_spread', 'prep_diversity', 'qo_chsh_early_ratio', 'kernel_order_compliance'
]

print(f"\n{'Feature':<25} {'Mean':>8} {'Std':>8} {'Min':>8} {'Max':>8}")
print("-" * 60)

for feat in feature_names:
    values = [f[feat] for f in folio_features.values()]
    print(f"{feat:<25} {np.mean(values):>8.3f} {np.std(values):>8.3f} {np.min(values):>8.3f} {np.max(values):>8.3f}")

# ============================================================
# TIER POSITION ORDERING CHECK
# ============================================================
print("\n--- Tier Position Ordering ---")

prep_positions = [f['prep_mean_position'] for f in folio_features.values()]
thermo_positions = [f['thermo_mean_position'] for f in folio_features.values()]
extended_positions = [f['extended_mean_position'] for f in folio_features.values()]

print(f"PREP mean position: {np.mean(prep_positions):.3f}")
print(f"THERMO mean position: {np.mean(thermo_positions):.3f}")
print(f"EXTENDED mean position: {np.mean(extended_positions):.3f}")

# Check ordering
prep_before_thermo = sum(1 for f in folio_features.values() if f['prep_mean_position'] < f['thermo_mean_position'])
thermo_before_extended = sum(1 for f in folio_features.values() if f['thermo_mean_position'] < f['extended_mean_position'])
prep_before_extended = sum(1 for f in folio_features.values() if f['prep_mean_position'] < f['extended_mean_position'])

n = len(folio_features)
print(f"\nOrdering compliance:")
print(f"  PREP < THERMO: {prep_before_thermo}/{n} ({100*prep_before_thermo/n:.1f}%)")
print(f"  THERMO < EXTENDED: {thermo_before_extended}/{n} ({100*thermo_before_extended/n:.1f}%)")
print(f"  PREP < EXTENDED: {prep_before_extended}/{n} ({100*prep_before_extended/n:.1f}%)")

# ============================================================
# SAVE RESULTS
# ============================================================
output = {
    'phase': 'PROCEDURAL_DIMENSION_EXTENSION',
    'test': 'procedural_features',
    'n_folios': len(folio_features),
    'feature_names': feature_names,
    'summary': {
        feat: {
            'mean': float(np.mean([f[feat] for f in folio_features.values()])),
            'std': float(np.std([f[feat] for f in folio_features.values()])),
            'min': float(np.min([f[feat] for f in folio_features.values()])),
            'max': float(np.max([f[feat] for f in folio_features.values()]))
        }
        for feat in feature_names
    },
    'tier_ordering': {
        'prep_before_thermo': prep_before_thermo,
        'thermo_before_extended': thermo_before_extended,
        'prep_before_extended': prep_before_extended,
        'total_folios': n
    },
    'folio_features': folio_features
}

output_path = PROJECT_ROOT / 'phases' / 'PROCEDURAL_DIMENSION_EXTENSION' / 'results' / 'procedural_features.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"\n\nResults saved to: {output_path}")
