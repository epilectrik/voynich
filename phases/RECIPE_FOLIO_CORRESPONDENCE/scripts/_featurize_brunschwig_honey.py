"""Apply the EXACT Phase 627 PL featurization pipeline to Brunschwig honey
recipes, then compute real distances to f75r in the same 8D space."""

import sys, json, re, math
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, 'C:/git/voynich')
sys.path.insert(0, 'C:/git/voynich/phases/PER_DOMAIN_BRIDGE_CALIBRATION/scripts')
sys.path.insert(0, 'C:/git/voynich/phases/RECIPE_FOLIO_CORRESPONDENCE/scripts')

from shared_628 import (
    TUNED_DIMS, build_pl_vector, build_v_vector,
    compute_residuals, standardize, euclidean_dist,
    load_pl_channel_features, load_b_operational_profiles,
    load_b_deployment_features, load_regime_mapping,
)

# ============================================================
# Phase 627 EXACT regex patterns (from pl_channel_features.py)
# ============================================================

HEAT_EN = re.compile(
    r'\b(fire|heat\w*|degree|gentle|strong|moderate|fierce|slow|'
    r'balneum|bath|bain-marie|water\s+bath|ashes?|ash\s+(?:fire|bed)|'
    r'sand|sand\s+bath|athanor|furnace|dung|horse\s+dung|quicklime|'
    r'cinericium|cupel|crucible|tripod|oven|charcoal|'
    r'digestion\s+[A-Z])\b',
    re.IGNORECASE
)

HEAT_TRANSITION = re.compile(
    r'\b(increase\s+(?:the\s+)?(?:fire|heat)|'
    r'reduce\s+(?:the\s+)?(?:fire|heat)|'
    r'decrease\s+(?:the\s+)?(?:fire|heat)|'
    r'change\s+(?:the\s+)?(?:fire|heat)|'
    r'gentle\s+fire|'
    r'strong(?:er)?\s+fire|'
    r'with\s+(?:a\s+)?(?:small|great|moderate|fierce)\s+fire|'
    r'first\s+degree|second\s+degree|third\s+degree|fourth\s+degree)\b',
    re.IGNORECASE
)

COLOR_EN = re.compile(
    r'\b(blackness|blackened|whiteness|whitened|redness|reddened|'
    r'nigredo|albedo|rubedo|citrin\w*|snow-white|charcoal|'
    r'scarlet)\b', re.IGNORECASE
)
COLOR_ADJ_EN = re.compile(
    r'\b(black|white|red|yellow|golden|pale|dark)\b(?=.*\b(?:color|appear|become|turn|sign|see))',
    re.IGNORECASE
)
CONSIST_EN = re.compile(
    r'\b(powder|powdery|pulverized|paste|wax-like|waxy|fusible|'
    r'fuse[ds]?|fusion|flow\w*|liquid|liquefied|crystallin\w*|'
    r'solid\w*|hardened|calx|earthy|oily|unctuous|'
    r'slimy|gummy|foliated)\b', re.IGNORECASE
)
VOLAT_EN = re.compile(
    r'\b(vapor\w*|fume[ds]?|smoke|smoking|volatile|volatilized|'
    r'sublimate[ds]?|flight|fleeing|ascending|rising|evaporate\w*)\b',
    re.IGNORECASE
)

TERM_EN = re.compile(
    r'\b(until|repeat\w*|reiterat\w*|as many times|so often|'
    r'continue\s+(?:this|the)|iterate\w*)\b', re.IGNORECASE
)

CORRECT_EN = re.compile(
    r'\b(error|errors?|erring|correct\w*|defect\w*|trouble|'
    r'fail\w*|beware\s+lest|wrong|mistaken|sophisticat\w*|'
    r'deceiv\w*|ruin\w*|burn\w*|combust\w*|start\s+over|'
    r'begin\s+again|lost|irrecoverable)\b', re.IGNORECASE
)


def featurize_text(text, label):
    """Apply Phase 627 regex featurization to a block of English text.
    Returns a dict with the same keys as PL channel signatures."""
    lines = [l for l in text.split('\n') if l.strip()]
    n_lines = len(lines)
    if n_lines == 0:
        n_lines = 1

    # T1: Heat
    total_heat = 0
    transition_count = 0
    for line in lines:
        if HEAT_EN.search(line):
            total_heat += 1
        if HEAT_TRANSITION.search(line):
            transition_count += 1

    # T2: Monitoring
    color_count = 0
    consistency_count = 0
    volatility_count = 0
    for line in lines:
        has_color = bool(COLOR_EN.search(line) or COLOR_ADJ_EN.search(line))
        has_consist = bool(CONSIST_EN.search(line))
        has_volat = bool(VOLAT_EN.search(line))
        if has_color:
            color_count += 1
        if has_consist:
            consistency_count += 1
        if has_volat:
            volatility_count += 1
    total_monitoring = color_count + consistency_count + volatility_count

    # T3: Termination
    total_termination = 0
    for line in lines:
        if TERM_EN.search(line):
            total_termination += 1

    # T4: Correction
    total_correction = 0
    for line in lines:
        if CORRECT_EN.search(line):
            total_correction += 1

    # Build channel signature (same formula as T5 in pl_channel_features.py)
    result = {
        'k_channel': {
            'heat_rate': total_heat / n_lines,
            'mean_heat_intensity': 0.0,  # would need mode classification
            'heat_transition_rate': transition_count / n_lines,
        },
        'e_channel': {
            'correction_rate': total_correction / n_lines,
            'recoverable_frac': 0.0,
            'process_drift_frac': 0.0,
        },
        'h_channel': {
            'monitoring_rate': total_monitoring / n_lines,
            'color_frac': color_count / max(total_monitoring, 1),
            'consistency_frac': consistency_count / max(total_monitoring, 1),
            'volatility_frac': volatility_count / max(total_monitoring, 1),
            'chain_rate': 0.0,
        },
        't_channel': {
            'termination_rate': total_termination / n_lines,
            'threshold_frac': 0.0,
        },
    }

    print(f"\n  {label} ({n_lines} lines):")
    print(f"    heat_rate           = {result['k_channel']['heat_rate']:.4f} ({total_heat} heat lines)")
    print(f"    heat_transition_rate= {result['k_channel']['heat_transition_rate']:.4f} ({transition_count})")
    print(f"    monitoring_rate     = {result['h_channel']['monitoring_rate']:.4f} ({total_monitoring})")
    print(f"    consistency_frac    = {result['h_channel']['consistency_frac']:.4f} ({consistency_count})")
    print(f"    correction_rate     = {result['e_channel']['correction_rate']:.4f} ({total_correction})")
    print(f"    termination_rate    = {result['t_channel']['termination_rate']:.4f} ({total_termination})")

    return result


# ============================================================
# Load Brunschwig English text and extract recipe passages
# ============================================================

with open('sources/brunschwig_1512/brunschwig_1512_english.txt', encoding='utf-8') as f:
    brun_lines = f.readlines()

brun_text = ''.join(brun_lines)

# Ch14: quinta essentia from honey (lines 5122-5165)
ch14_text = ''.join(brun_lines[5121:5165])

# Ch28: distilling honey, 9x boil/skim + balneum 40 days (lines 6182-6222)
ch28_text = ''.join(brun_lines[6181:6222])

# Book5: aurum potabile = PL Ch19 parallel (lines 24191-24210)
book5_text = ''.join(brun_lines[24191:24210])

# Combined: all three honey passages
combined_text = ch14_text + '\n' + ch28_text + '\n' + book5_text

print("=" * 70)
print("FEATURIZATION (Phase 627 exact regexes)")
print("=" * 70)

feats_ch14 = featurize_text(ch14_text, "Brunschwig Ch14 (quinta essentia from honey)")
feats_ch28 = featurize_text(ch28_text, "Brunschwig Ch28 (distilling honey, 9x)")
feats_book5 = featurize_text(book5_text, "Brunschwig Book5 (aurum potabile)")
feats_combined = featurize_text(combined_text, "Brunschwig COMBINED")

# ============================================================
# Load PL Ch19 and show its profile for comparison
# ============================================================

pl_feats = load_pl_channel_features()
per_ch = pl_feats['T5_channel_signatures']['per_chapter']
ch19 = per_ch[146]  # distillation family, chapter_number=19

print("\n" + "=" * 70)
print("PL Ch19 PROFILE (for comparison)")
print("=" * 70)
print(f"\n  PL Ch19 ({ch19['n_lines']} lines):")
print(f"    heat_rate           = {ch19['k_channel']['heat_rate']:.4f}")
print(f"    heat_transition_rate= {ch19['k_channel']['heat_transition_rate']:.4f}")
print(f"    monitoring_rate     = {ch19['h_channel']['monitoring_rate']:.4f}")
print(f"    consistency_frac    = {ch19['h_channel']['consistency_frac']:.4f}")
print(f"    correction_rate     = {ch19['e_channel']['correction_rate']:.4f}")
print(f"    termination_rate    = {ch19['t_channel']['termination_rate']:.4f}")

# ============================================================
# Compute distances to f75r using the SAME residual matching
# ============================================================

print("\n" + "=" * 70)
print("DISTANCE TO f75r (8D residual matching)")
print("=" * 70)

# Load V-side data
op_profiles = load_b_operational_profiles()
deploy_features, _ = load_b_deployment_features()
regime_map = load_regime_mapping()
r1_folios = sorted(f for f, r in regime_map.items() if r == 'REGIME_1')

print(f"\nR1 folios: {len(r1_folios)}")

# Get all distillation chapters
dist_chs = [c for c in per_ch if c.get('family') == 'distillation']
ch19_dist_idx = None
for i, c in enumerate(dist_chs):
    if c['chapter_idx'] == 146:
        ch19_dist_idx = i
        break

print(f"Distillation chapters: {len(dist_chs)}, Ch19 at dist_idx={ch19_dist_idx}")

# Build vectors for all distillation chapters + Brunschwig variants
pl_vecs = [build_pl_vector(c, TUNED_DIMS) for c in dist_chs]
v_vecs = [build_v_vector(f, op_profiles, deploy_features, TUNED_DIMS) for f in r1_folios]

# Also build vectors for Brunschwig recipes using the same build_pl_vector
brun_recipes = {
    'Brun_Ch14': feats_ch14,
    'Brun_Ch28': feats_ch28,
    'Brun_Book5': feats_book5,
    'Brun_COMBINED': feats_combined,
}

brun_vecs = {}
for name, feats in brun_recipes.items():
    vec = build_pl_vector(feats, TUNED_DIMS)
    brun_vecs[name] = vec

# Apply sign flips to PL side (and Brunschwig, since they're on same side)
for i in range(len(pl_vecs)):
    for d_idx, (_, _, sign) in enumerate(TUNED_DIMS):
        pl_vecs[i][d_idx] *= sign

for name in brun_vecs:
    for d_idx, (_, _, sign) in enumerate(TUNED_DIMS):
        brun_vecs[name][d_idx] *= sign

# Now compute residuals for PL (within distillation family)
pl_resid = compute_residuals(pl_vecs)
v_resid = compute_residuals(v_vecs)

# For Brunschwig: compute residual relative to the SAME distillation mean
n_pl = len(pl_vecs)
d = len(TUNED_DIMS)
pl_mean = [sum(pl_vecs[i][j] for i in range(n_pl)) / n_pl for j in range(d)]

brun_resid = {}
for name, vec in brun_vecs.items():
    brun_resid[name] = [vec[j] - pl_mean[j] for j in range(d)]

# Standardize jointly: all PL residuals + all V residuals
all_vecs = pl_resid + v_resid
all_std = standardize(all_vecs)
pl_std = all_std[:len(pl_resid)]
v_std = all_std[len(pl_resid):]

# For Brunschwig: standardize using the same mean/sd as the joint set
# We need the mean and sd from the joint standardization
n_all = len(all_vecs)
for dim_idx in range(d):
    vals = [v[dim_idx] for v in all_vecs]
    mu = sum(vals) / n_all
    var = sum((x - mu) ** 2 for x in vals) / n_all
    sd = math.sqrt(var) if var > 0 else 1.0
    for name in brun_resid:
        if dim_idx == 0:
            brun_resid[name] = list(brun_resid[name])  # ensure mutable
        # Standardize Brunschwig residual using same mu/sd
        # Wait - we need the original (non-standardized) residual
        pass

# Actually, let's just insert Brunschwig into the joint standardization
# Redo: put Brunschwig residuals into the mix
all_vecs_with_brun = pl_resid + list(brun_resid.values()) + v_resid
all_std2 = standardize(all_vecs_with_brun)

n_pl_total = len(pl_resid)
n_brun = len(brun_resid)
n_v = len(v_resid)

pl_std2 = all_std2[:n_pl_total]
brun_std2 = all_std2[n_pl_total:n_pl_total + n_brun]
v_std2 = all_std2[n_pl_total + n_brun:]

brun_names = list(brun_resid.keys())

# Find f75r index
f75r_idx = r1_folios.index('f75r')

# ============================================================
# RESULTS
# ============================================================

print("\n--- Distances to f75r ---")
print(f"{'Source':20s} {'Distance':>10s} {'Rank in R1':>10s}")
print("-" * 45)

# PL Ch19
ch19_dist = euclidean_dist(pl_std2[ch19_dist_idx], v_std2[f75r_idx])

# All PL distillation chapters to f75r (for rank)
pl_dists_to_f75r = []
for i, c in enumerate(dist_chs):
    d_val = euclidean_dist(pl_std2[i], v_std2[f75r_idx])
    pl_dists_to_f75r.append((c['chapter_number'], d_val))

pl_dists_to_f75r.sort(key=lambda x: x[1])
ch19_rank = [i for i, (num, _) in enumerate(pl_dists_to_f75r) if num == 19][0] + 1
print(f"  {'PL Ch19':20s} {ch19_dist:10.4f} {ch19_rank:>5d}/16")

# Brunschwig recipes
for i, name in enumerate(brun_names):
    d_val = euclidean_dist(brun_std2[i], v_std2[f75r_idx])
    # Rank: how many PL chapters are closer?
    n_closer = sum(1 for _, pd in pl_dists_to_f75r if pd < d_val)
    print(f"  {name:20s} {d_val:10.4f} {n_closer + 1:>5d}/16")

# Show full ranking
print("\n--- Full ranking: all PL distillation chapters + Brunschwig to f75r ---")
all_dists = []
for i, c in enumerate(dist_chs):
    d_val = euclidean_dist(pl_std2[i], v_std2[f75r_idx])
    all_dists.append((f"PL Ch{c['chapter_number']}", d_val))

for i, name in enumerate(brun_names):
    d_val = euclidean_dist(brun_std2[i], v_std2[f75r_idx])
    all_dists.append((name, d_val))

all_dists.sort(key=lambda x: x[1])
for rank, (name, d_val) in enumerate(all_dists, 1):
    marker = " <<<" if 'Ch19' in name or 'Brun' in name else ""
    print(f"  {rank:2d}. {name:20s} {d_val:.4f}{marker}")
