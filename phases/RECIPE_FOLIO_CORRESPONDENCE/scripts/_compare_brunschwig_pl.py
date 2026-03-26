"""Compare PL Ch19 vs Brunschwig honey recipes on the same 8D feature space
used for f75r matching. Computes PL-style channel features for Brunschwig
text and checks which is a stronger match to f75r."""

import sys
sys.path.insert(0, 'C:/git/voynich')
sys.path.insert(0, 'C:/git/voynich/phases/PER_DOMAIN_BRIDGE_CALIBRATION/scripts')
sys.path.insert(0, 'C:/git/voynich/phases/RECIPE_FOLIO_CORRESPONDENCE/scripts')

import json
import re
from pathlib import Path
from collections import Counter

from shared_628 import (
    TUNED_DIMS, build_v_vector,
    load_b_operational_profiles, load_b_deployment_features,
    load_pl_channel_features, euclidean_dist,
)

# ============================================================
# 1. Load PL Ch19 feature profile (already computed)
# ============================================================
pl_feats = load_pl_channel_features()
per_ch = pl_feats['T5_channel_signatures']['per_chapter']

ch19 = None
for ch in per_ch:
    if ch.get('chapter') == 19 and ch.get('part') == 'practica':
        ch19 = ch
        break

if ch19 is None:
    # Try different keys
    for ch in per_ch:
        if '19' in str(ch.get('chapter', '')):
            ch19 = ch
            print(f"Found Ch19 with key: {ch}")
            break

if ch19 is None:
    print("ERROR: Could not find PL Ch19 in channel features")
    print(f"Available chapters (first 10): {[c.get('chapter') for c in per_ch[:10]]}")
    sys.exit(1)

print("=" * 70)
print("PL Ch19 CHANNEL FEATURES (from Phase 628)")
print("=" * 70)

# Extract the 8 PL-side features
for pl_feat, v_feat, sign in TUNED_DIMS:
    val = None
    for ch_key in ['k_channel', 'h_channel', 'e_channel', 't_channel']:
        ch_data = ch19.get(ch_key, {})
        if pl_feat in ch_data:
            val = ch_data[pl_feat]
            break
    if val is None:
        val = ch19.get(pl_feat, 'NOT FOUND')
    print(f"  {pl_feat:25s} = {val}")

# ============================================================
# 2. Compute same features for Brunschwig recipes from TEXT
# ============================================================
# We need to compute heat_rate, monitoring_rate, correction_rate,
# termination_rate, consistency_frac, heat_transition_rate
# from the English text using keyword counting (same method as PL featurization)

# Load the PL featurization method to understand what each feature means
# From Phase 602 pseudo_lull_structural_profile.json
pl_profile_path = Path('phases/PSEUDO_LULL_CHARACTERIZATION/results/pseudo_lull_structural_profile.json')
with open(pl_profile_path) as f:
    pl_profile = json.load(f)

# Check what E3_operations looks like to understand feature computation
print("\n" + "=" * 70)
print("PL FEATURE DEFINITIONS (from E3)")
print("=" * 70)

if 'E3_operations' in pl_profile:
    e3 = pl_profile['E3_operations']
    print(f"Keys: {list(e3.keys())[:15]}")
elif 'E3' in pl_profile:
    e3 = pl_profile['E3']
    print(f"Keys: {list(e3.keys())[:15]}")

# Let's look at what features Ch19 actually has
print("\n" + "=" * 70)
print("Ch19 FULL FEATURE SET")
print("=" * 70)
for key in sorted(ch19.keys()):
    val = ch19[key]
    if isinstance(val, dict):
        print(f"  {key}:")
        for k2, v2 in sorted(val.items()):
            print(f"    {k2:30s} = {v2}")
    else:
        print(f"  {key:30s} = {val}")

# ============================================================
# 3. Count operational keywords in Brunschwig recipes
# ============================================================

# Read English translation
with open('sources/brunschwig_1512/brunschwig_1512_english.txt', encoding='utf-8') as f:
    brun_text = f.read()

# Extract the three honey-related passages
# Ch14: lines 5122-5160 (quinta essentia from honey)
# Ch28: lines 6182-6221 (distilling honey, nine times)
# Book5: lines 24192-24202 (aurum potabile, PL Ch19 parallel)

lines = brun_text.split('\n')

ch14_text = '\n'.join(lines[5121:5165])
ch28_text = '\n'.join(lines[6181:6222])
book5_text = '\n'.join(lines[24191:24210])

# Combined honey recipe text
combined_text = ch14_text + '\n' + ch28_text + '\n' + book5_text

print("\n" + "=" * 70)
print("BRUNSCHWIG HONEY RECIPE TEXTS")
print("=" * 70)
print(f"\nCh14 ({len(ch14_text)} chars): quinta essentia from honey")
print(f"Ch28 ({len(ch28_text)} chars): distilling honey, nine times boil/skim")
print(f"Book5 ({len(book5_text)} chars): aurum potabile = PL Ch19 parallel")
print(f"Combined: {len(combined_text)} chars")

# Keyword-based operational feature extraction
# These mirror the PL featurization categories

HEAT_KEYWORDS = [
    'distill', 'fire', 'heat', 'warm', 'burn', 'boil', 'cook', 'hot',
    'furnace', 'oven', 'coals', 'balneum', 'balneo', 'ash', 'sand',
    'calcin', 'gentle fire', 'strong fire', 'dung',
]

MONITOR_KEYWORDS = [
    'observe', 'note', 'watch', 'test', 'taste', 'see', 'know',
    'recognize', 'examine', 'check', 'look', 'color', 'clear',
    'thick', 'when', 'until', 'sign', 'proper', 'ready', 'enough',
]

CORRECTION_KEYWORDS = [
    'pour', 'add', 'put', 'place', 'mix', 'stir', 'wash',
    'strain', 'filter', 'skim', 'remove', 'separate', 'divide',
    'clean', 'press', 'squeeze', 'extract',
]

TERMINATION_KEYWORDS = [
    'stop', 'done', 'complete', 'finish', 'end', 'ready',
    'thus', 'proper', 'enough', 'preserve', 'keep', 'seal',
    'stored',
]

ITERATION_KEYWORDS = [
    'again', 'repeat', 'times', 'nine', 'seven', 'return',
    'reiterate', 'cycle', 'once more', 'do so', 'as before',
    'each time',
]

def count_keywords(text, keywords):
    text_lower = text.lower()
    count = 0
    for kw in keywords:
        count += len(re.findall(r'\b' + re.escape(kw) + r'\b', text_lower))
    return count

def compute_recipe_features(text, label):
    """Compute PL-style operational features from recipe text."""
    words = text.lower().split()
    n_words = len(words)

    heat = count_keywords(text, HEAT_KEYWORDS)
    monitor = count_keywords(text, MONITOR_KEYWORDS)
    correct = count_keywords(text, CORRECTION_KEYWORDS)
    terminate = count_keywords(text, TERMINATION_KEYWORDS)
    iterate = count_keywords(text, ITERATION_KEYWORDS)

    total_ops = heat + monitor + correct + terminate + iterate
    if total_ops == 0:
        total_ops = 1

    # Compute rates (fraction of operational keywords)
    heat_rate = heat / total_ops
    monitor_rate = monitor / total_ops
    correct_rate = correct / total_ops
    terminate_rate = terminate / total_ops
    iterate_rate = iterate / total_ops

    # Heat transition: how many transitions between heat-related and non-heat sentences?
    sentences = re.split(r'[.;!?]', text)
    heat_transitions = 0
    prev_has_heat = False
    for s in sentences:
        has_heat = any(kw in s.lower() for kw in ['distill', 'fire', 'heat', 'warm', 'boil', 'balneum', 'balneo'])
        if has_heat != prev_has_heat and prev_has_heat is not None:
            heat_transitions += 1
        prev_has_heat = has_heat
    heat_transition_rate = heat_transitions / max(len(sentences), 1)

    # Consistency: how repetitive are the operations?
    op_sequence = []
    for s in sentences:
        s_lower = s.lower()
        if any(kw in s_lower for kw in ['distill', 'fire', 'heat']):
            op_sequence.append('H')
        elif any(kw in s_lower for kw in ['observe', 'test', 'taste', 'when', 'until']):
            op_sequence.append('M')
        elif any(kw in s_lower for kw in ['pour', 'add', 'put', 'mix']):
            op_sequence.append('C')
        else:
            op_sequence.append('O')

    if len(op_sequence) > 1:
        same_pairs = sum(1 for i in range(len(op_sequence)-1) if op_sequence[i] == op_sequence[i+1])
        consistency_frac = same_pairs / (len(op_sequence) - 1)
    else:
        consistency_frac = 0.0

    print(f"\n  {label}:")
    print(f"    Words: {n_words}, Sentences: {len(sentences)}")
    print(f"    Heat:      {heat:3d} ({heat_rate:.3f})")
    print(f"    Monitor:   {monitor:3d} ({monitor_rate:.3f})")
    print(f"    Correct:   {correct:3d} ({correct_rate:.3f})")
    print(f"    Terminate: {terminate:3d} ({terminate_rate:.3f})")
    print(f"    Iterate:   {iterate:3d} ({iterate_rate:.3f})")
    print(f"    Heat transitions: {heat_transitions} (rate={heat_transition_rate:.3f})")
    print(f"    Consistency frac: {consistency_frac:.3f}")

    return {
        'heat_rate': heat_rate,
        'monitoring_rate': monitor_rate,
        'correction_rate': correct_rate,
        'termination_rate': terminate_rate,
        'consistency_frac': consistency_frac,
        'heat_transition_rate': heat_transition_rate,
    }

print("\n" + "=" * 70)
print("BRUNSCHWIG RECIPE FEATURE PROFILES")
print("=" * 70)

feats_ch14 = compute_recipe_features(ch14_text, "Ch14 (quinta essentia from honey)")
feats_ch28 = compute_recipe_features(ch28_text, "Ch28 (distilling honey, 9x)")
feats_book5 = compute_recipe_features(book5_text, "Book5 (aurum potabile = PL Ch19 parallel)")
feats_combined = compute_recipe_features(combined_text, "COMBINED (all honey recipes)")

# ============================================================
# 4. Load f75r V-side profile and compute distances
# ============================================================

op_profiles = load_b_operational_profiles()
deploy_features, _ = load_b_deployment_features()

f75r_vec = build_v_vector('f75r', op_profiles, deploy_features, TUNED_DIMS)

print("\n" + "=" * 70)
print("f75r V-SIDE FEATURE VECTOR")
print("=" * 70)
for (pl_feat, v_feat, sign), val in zip(TUNED_DIMS, f75r_vec):
    print(f"  {v_feat:40s} = {val:.4f}")

# ============================================================
# 5. Build PL-style vectors and compute distances
# ============================================================
# The PL features stored in channel signatures are already normalized
# per the Phase 627 pipeline. We can't directly compare raw keyword
# counts to those. Instead, let's look at PL Ch19's RANK among all
# PL distillation chapters and see if Brunschwig would rank similarly.

print("\n" + "=" * 70)
print("PL Ch19 FEATURES vs BRUNSCHWIG FEATURES (relative comparison)")
print("=" * 70)

# Get PL Ch19 values
ch19_feats = {}
for pl_feat, v_feat, sign in TUNED_DIMS:
    val = None
    for ch_key in ['k_channel', 'h_channel', 'e_channel', 't_channel']:
        ch_data = ch19.get(ch_key, {})
        if pl_feat in ch_data:
            val = ch_data[pl_feat]
            break
    if val is None:
        val = ch19.get(pl_feat, 0.0)
    ch19_feats[pl_feat] = val

# Compare directions
print(f"\n{'Feature':25s} {'PL_Ch19':>10s} {'Brun_Ch28':>10s} {'Brun_Book5':>10s} {'Brun_Comb':>10s} {'Same dir?':>10s}")
print("-" * 75)
for pl_feat, v_feat, sign in TUNED_DIMS:
    pl_val = ch19_feats.get(pl_feat, 0.0)
    b28_val = feats_ch28.get(pl_feat, 0.0)
    b5_val = feats_book5.get(pl_feat, 0.0)
    bc_val = feats_combined.get(pl_feat, 0.0)

    # Can't directly compare scales, but can compare relative magnitudes
    print(f"  {pl_feat:25s} {pl_val:10.4f} {b28_val:10.4f} {b5_val:10.4f} {bc_val:10.4f}")

# ============================================================
# 6. Compare within PL distillation family
# ============================================================
print("\n" + "=" * 70)
print("PL Ch19 RANK AMONG DISTILLATION CHAPTERS")
print("=" * 70)

dist_chapters = [ch for ch in per_ch if ch.get('family') == 'distillation']
print(f"Total distillation chapters: {len(dist_chapters)}")

for pl_feat, v_feat, sign in TUNED_DIMS:
    vals = []
    for ch in dist_chapters:
        val = None
        for ch_key in ['k_channel', 'h_channel', 'e_channel', 't_channel']:
            ch_data = ch.get(ch_key, {})
            if pl_feat in ch_data:
                val = ch_data[pl_feat]
                break
        if val is None:
            val = ch.get(pl_feat, 0.0)
        vals.append(val)

    ch19_val = ch19_feats[pl_feat]
    rank = sum(1 for v in vals if v <= ch19_val)
    pct = 100 * rank / len(vals) if vals else 0
    print(f"  {pl_feat:25s}: Ch19={ch19_val:.4f}  rank={rank}/{len(vals)} ({pct:.0f}th percentile)")

# ============================================================
# 7. Direct comparison: what does PL Ch19 look like operationally?
# ============================================================
print("\n" + "=" * 70)
print("QUALITATIVE COMPARISON")
print("=" * 70)

print("""
PL Ch19 recipe profile:
  - HIGH heat (9x repeated distillation = sustained thermal ops)
  - LOW monitoring (brief recipe, few quality checks)
  - MODERATE correction (adding honey/wax, fermentation step)
  - LOW termination (no explicit stopping criteria)
  - HIGH consistency (same operation repeated)
  - HIGH heat_transition (distill->ferment->distill cycling)

Brunschwig Ch28 profile:
  - HIGH heat (9x boil/skim + balneum mariae + distillation)
  - MODERATE monitoring (color/texture checks, fraction separation)
  - HIGH correction (pour water, skim, add cloths, change receivers)
  - MODERATE termination (fraction endpoints, 40-day circulation end)
  - MODERATE consistency (varied operations within the cycle)
  - HIGH heat_transition (boil->cool->circulate->distill->ash)

Brunschwig Book5 profile:
  - HIGH heat (aqua vite distillation + balneum + dung)
  - LOW monitoring (brief, compressed)
  - LOW correction (place honeycomb, set warmth)
  - LOW termination ("then it will be proper")
  - HIGH consistency (ferment+distill repeated)
  - HIGH heat_transition (distill->putrefy->distill cycling)

KEY INSIGHT: Book5 is the closest to PL Ch19 because both are
COMPRESSED recipes with the same structure (high heat, low monitoring,
high consistency, cycling). Ch28 adds practical detail that INCREASES
monitoring and correction -- making it look more like an EXPANDED
operational manual.

If the Voynich is the procedural companion, its profile should look
more like Ch28 (high monitoring, varied corrections) than like PL Ch19
or Book5 (compressed, low monitoring).
""")

# Check f75r operational profile
f75r_prof = op_profiles.get('f75r', {})
print("f75r operational profile:")
for k, v in sorted(f75r_prof.items()):
    print(f"  {k:30s} = {v}")
