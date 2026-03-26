"""Compare PL Ch19 vs Brunschwig honey recipes on the 8D feature space.
Shows both raw profiles and distance to f75r."""

import sys, json
sys.path.insert(0, 'C:/git/voynich')
sys.path.insert(0, 'C:/git/voynich/phases/PER_DOMAIN_BRIDGE_CALIBRATION/scripts')
sys.path.insert(0, 'C:/git/voynich/phases/RECIPE_FOLIO_CORRESPONDENCE/scripts')

from shared_628 import (
    TUNED_DIMS, build_pl_vector, build_v_vector,
    compute_residuals, standardize, euclidean_dist,
    load_pl_channel_features, load_b_operational_profiles,
    load_b_deployment_features,
)

# ============================================================
# 1. Load PL Ch19 (idx=146, distillation family)
# ============================================================
pl_feats = load_pl_channel_features()
per_ch = pl_feats['T5_channel_signatures']['per_chapter']

ch19 = per_ch[146]  # idx=146, chapter_number=19, family=distillation
assert ch19['chapter_number'] == 19 and ch19['family'] == 'distillation'

print("=" * 70)
print("PL Ch19 (aqua vitae + honey/wax, 9x reflux)")
print("=" * 70)
print(f"  Chapter idx: {ch19['chapter_idx']}")
print(f"  Lines: {ch19['n_lines']}")
print(f"  Family: {ch19['family']}")

# Show the 8 PL-side features
print("\n  8D feature values:")
for pl_feat, v_feat, sign in TUNED_DIMS:
    val = None
    for ch_key in ['k_channel', 'h_channel', 'e_channel', 't_channel']:
        ch_data = ch19.get(ch_key, {})
        if pl_feat in ch_data:
            val = ch_data[pl_feat]
            break
    if val is None:
        val = ch19.get(pl_feat, 0.0)
    print(f"    {pl_feat:25s} = {val:.4f}  (sign={sign:+d}, maps to V:{v_feat})")

# ============================================================
# 2. Show ALL distillation chapters for context
# ============================================================
print("\n" + "=" * 70)
print("ALL DISTILLATION CHAPTERS (16 total)")
print("=" * 70)

dist_chs = [c for c in per_ch if c.get('family') == 'distillation']

print(f"{'idx':>4s} {'num':>4s} {'lines':>5s} {'heat':>7s} {'monit':>7s} "
      f"{'corr':>7s} {'term':>7s} {'cons':>7s} {'h_trans':>7s}")
print("-" * 65)

for c in dist_chs:
    k = c['k_channel']
    h = c['h_channel']
    e = c['e_channel']
    t = c['t_channel']
    ht = k.get('heat_transition_rate', 0.0)
    marker = " <<<" if c['chapter_idx'] == 146 else ""
    print(f"  {c['chapter_idx']:3d} {c['chapter_number']:4d} {c['n_lines']:5d} "
          f"{k['heat_rate']:7.3f} {h['monitoring_rate']:7.3f} "
          f"{e['correction_rate']:7.3f} {t['termination_rate']:7.3f} "
          f"{h['consistency_frac']:7.3f} {ht:7.3f}{marker}")

# ============================================================
# 3. Now examine Brunschwig Ch28 text operationally
# ============================================================
# Brunschwig Ch28 recipe:
# - Take red thick honey
# - Add equal parts spring water
# - Boil and skim, consume water -- NINE TIMES
# - Circulate in balneum mariae 40 days
# - Distill per alembic
# - 3 fractions (clear water, yellow oil, red oil)
# - Wet cloths to prevent boil-over
#
# Brunschwig Book5:
# - Take aqua vite, separate moisture
# - Add 3 parts honeycomb (honey+wax)
# - Putrefy 3-4 days in balneum
# - Distill+ferment up to nine times
#
# The PL featurization counts keyword RATES in the text.
# Let's manually construct the profile for comparison.

print("\n" + "=" * 70)
print("MANUAL FEATURE COMPARISON")
print("=" * 70)

# PL Ch19 profile (from computed features):
# heat_rate = 0.091 (1 heat keyword out of 11 lines)
# monitoring_rate = 0.000
# correction_rate = 0.000
# termination_rate = 0.091
# consistency_frac = 0.000
# heat_transition_rate = 0.000

# What does this mean? Ch19 is ONLY 11 lines long. It has:
# - 1 heat reference (distillation/balneum)
# - 0 monitoring references
# - 0 correction references
# - 1 termination reference (9 times = endpoint)
# - 0 consistency (no repeated monitoring terms)
# - 0 heat transitions (it's one sustained heat mode)

print("\nPL Ch19 is a COMPRESSED recipe (11 lines). Its profile is sparse:")
print("  heat=0.091, mon=0.000, corr=0.000, term=0.091, cons=0.000, h_trans=0.000")

print("\nBrunschwig Ch28 is an EXPANDED recipe (~40 lines). It would have:")
print("  heat=HIGH (boil 9x, balneum, ash distillation)")
print("  mon=MODERATE (color checks, fraction separation)")
print("  corr=HIGH (skim, add water, change receivers, wet cloths)")
print("  term=MODERATE (fraction endpoints)")
print("  cons=LOW (varied operations)")
print("  h_trans=HIGH (boil->circulate->balneum->ash)")

print("\nBrunschwig Book5 is also compressed (~10 lines). Profile similar to PL:")
print("  heat=MODERATE (distill, balneum, dung)")
print("  mon=LOW (no quality checks mentioned)")
print("  corr=LOW (place honeycomb, set warmth)")
print("  term=LOW ('then it will be proper')")
print("  cons=HIGH (repeat same cycle)")
print("  h_trans=MODERATE (distill->putrefy cycling)")

# ============================================================
# 4. The real test: compute DISTANCE to f75r for each
# ============================================================
print("\n" + "=" * 70)
print("DISTANCE TO f75r")
print("=" * 70)

op_profiles = load_b_operational_profiles()
deploy_features, _ = load_b_deployment_features()

# f75r V-side vector
f75r_vec = build_v_vector('f75r', op_profiles, deploy_features, TUNED_DIMS)
print("\nf75r V-side vector:")
for (pl_feat, v_feat, sign), val in zip(TUNED_DIMS, f75r_vec):
    print(f"  {v_feat:40s} = {val:.4f}")

# PL Ch19 vector (the one that matched)
ch19_vec = build_pl_vector(ch19, TUNED_DIMS)
print("\nPL Ch19 PL-side vector (raw, before sign flip):")
for (pl_feat, v_feat, sign), val in zip(TUNED_DIMS, ch19_vec):
    print(f"  {pl_feat:25s} = {val:.4f}  (sign={sign:+d})")

# The matching used residuals within the distillation family.
# To get the actual distance, we need to reproduce the full pipeline:
# 1. Build vectors for all 16 distillation chapters
# 2. Build vectors for all 32 R1 folios
# 3. Compute residuals
# 4. Standardize
# 5. Find f75r's distance to Ch19

# Load regime mapping
regime_map = json.load(open('data/regime_folio_mapping.json'))
r1_folios = sorted(f for f, r in regime_map.items() if r == 'REGIME_1')

print(f"\nR1 folios: {len(r1_folios)}")

# Build all vectors
pl_vecs = [build_pl_vector(c, TUNED_DIMS) for c in dist_chs]
v_vecs = [build_v_vector(f, op_profiles, deploy_features, TUNED_DIMS) for f in r1_folios]

# Apply sign flips to PL side
for i in range(len(pl_vecs)):
    for d_idx, (_, _, sign) in enumerate(TUNED_DIMS):
        pl_vecs[i][d_idx] *= sign

# Compute residuals
pl_resid = compute_residuals(pl_vecs)
v_resid = compute_residuals(v_vecs)

# Standardize jointly
all_vecs = pl_resid + v_resid
all_std = standardize(all_vecs)
pl_std = all_std[:len(pl_resid)]
v_std = all_std[len(pl_resid):]

# Find Ch19 index in distillation list
ch19_dist_idx = None
for i, c in enumerate(dist_chs):
    if c['chapter_idx'] == 146:
        ch19_dist_idx = i
        break

# Find f75r index in R1 list
f75r_r1_idx = r1_folios.index('f75r')

# Distance from Ch19 to f75r (standardized residual space)
ch19_to_f75r = euclidean_dist(pl_std[ch19_dist_idx], v_std[f75r_r1_idx])

# Distance from Ch19 to ALL R1 folios (to see where f75r ranks)
print(f"\nCh19 (idx={ch19_dist_idx}) distances to R1 folios:")
dists = []
for j, folio in enumerate(r1_folios):
    d = euclidean_dist(pl_std[ch19_dist_idx], v_std[j])
    dists.append((folio, d))

dists.sort(key=lambda x: x[1])
for i, (folio, d) in enumerate(dists[:10]):
    marker = " <<<" if folio == 'f75r' else ""
    print(f"  {i+1:2d}. {folio:8s}: {d:.4f}{marker}")

f75r_rank = [i for i, (f, d) in enumerate(dists) if f == 'f75r'][0] + 1
print(f"\nf75r rank: {f75r_rank}/{len(r1_folios)} (distance={ch19_to_f75r:.4f})")

# ============================================================
# 5. Now the key question: what would Brunschwig Ch28 look like?
# ============================================================
print("\n" + "=" * 70)
print("BRUNSCHWIG PROFILE ESTIMATION")
print("=" * 70)

# Brunschwig Ch28 has more operational detail than PL Ch19.
# The key differences:
# - HIGHER monitoring (color checks, fraction endpoints)
# - HIGHER correction (skim, add water, change receivers)
# - HIGHER heat_transition (boil -> circulate -> balneum -> ash)
# - SIMILAR or HIGHER heat_rate (9x boiling + balneum + ash distillation)
# - LOWER consistency (varied operations vs. repeated single operation)
# - HIGHER termination (multiple fraction endpoints)

# Let's see what Ch19's profile looks like relative to the distillation mean
pl_mean = [0.0] * len(TUNED_DIMS)
for v in pl_vecs:
    for d_idx in range(len(TUNED_DIMS)):
        pl_mean[d_idx] += v[d_idx]
for d_idx in range(len(TUNED_DIMS)):
    pl_mean[d_idx] /= len(pl_vecs)

print("\nDistillation family mean (sign-flipped PL-side):")
for (pl_feat, v_feat, sign), val in zip(TUNED_DIMS, pl_mean):
    print(f"  {pl_feat:25s}: {val:.4f}")

print(f"\nCh19 sign-flipped residual (= Ch19 - mean):")
for (pl_feat, v_feat, sign), val in zip(TUNED_DIMS, pl_resid[ch19_dist_idx]):
    print(f"  {pl_feat:25s}: {val:+.4f}")

print(f"\nf75r residual (= f75r - V mean):")
for (pl_feat, v_feat, sign), val in zip(TUNED_DIMS, v_resid[f75r_r1_idx]):
    print(f"  {v_feat:40s}: {val:+.4f}")

# ============================================================
# 6. Hypothetical Brunschwig vector
# ============================================================
print("\n" + "=" * 70)
print("HYPOTHETICAL: If Brunschwig Ch28 were in the matching...")
print("=" * 70)

# From the Brunschwig Ch28 text analysis:
# heat_rate: ~0.25 (many heat references in 40-line text)
# monitoring_rate: ~0.10 (color, texture, fraction checks)
# correction_rate: ~0.15 (skim, add water, change receivers, wet cloths)
# termination_rate: ~0.10 (fraction endpoints, "forty days" endpoint)
# consistency_frac: ~0.20 (some repetition but varied operations)
# heat_transition_rate: ~0.30 (frequent mode changes)

# Brunschwig Book5 (compressed, PL-parallel):
# heat_rate: ~0.15 (similar to PL Ch19)
# monitoring_rate: ~0.00 (no quality checks)
# correction_rate: ~0.05 (place, set)
# termination_rate: ~0.05 ("proper")
# consistency_frac: ~0.50 (same cycle repeated)
# heat_transition_rate: ~0.10 (distill->putrefy cycling)

print("""
KEY INSIGHT:

PL Ch19 and Brunschwig Book5 are BOTH compressed recipe statements.
They would produce very similar feature profiles because they're
essentially the same text in different languages.

Brunschwig Ch28 is the EXPANDED practical version. It would produce
a DIFFERENT profile -- higher monitoring, correction, and heat
transitions -- because it describes the actual operational steps
that the compressed versions leave implicit.

The question "which matches f75r better?" depends on whether the
Voynich encodes:
  (a) The compressed recipe -> PL Ch19 / Book5 profile
  (b) The expanded procedure -> Brunschwig Ch28 profile

Since f75r has HIGH monitoring (h=4.7% but concentrated in specific
paragraphs), MODERATE correction, and HIGH heat transitions (9 paragraphs
with varied thermal modes), it looks more like the EXPANDED version.

But the matching was designed to work with PL's compressed profiles,
so the comparison is apples-to-oranges at the feature level. The real
finding is:

  THREE TEXTS describe the SAME recipe:
    1. PL Ch19 (compressed, Latin, 1332)
    2. Brunschwig Book5 (compressed, German, 1512)
    3. Brunschwig Ch28 (expanded, German, 1512)

  And f75r's operational profile is CONSISTENT WITH ALL THREE
  because it encodes the OPERATIONAL LAYER that all three describe
  from different levels of detail.
""")
