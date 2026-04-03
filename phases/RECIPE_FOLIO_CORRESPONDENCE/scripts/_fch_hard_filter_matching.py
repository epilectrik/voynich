"""Use fch (mercury marker) as a hard filter to extend recipe matching.

7 unmatched folios contain fch (predicting mercury involvement).
6-8 higher Mercuriorum chapters (Ch40-Ch52, previously classified as 'theoretical')
contain genuine procedural content.

This script runs 8D residual matching between these chapters and folios."""

import sys, io, json, math
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, 'C:/git/voynich')
sys.path.insert(0, 'C:/git/voynich/phases/PER_DOMAIN_BRIDGE_CALIBRATION/scripts')
sys.path.insert(0, 'C:/git/voynich/phases/RECIPE_FOLIO_CORRESPONDENCE/scripts')

from shared_628 import (
    TUNED_DIMS,
    load_pl_channel_features,
    load_b_operational_profiles,
    load_b_deployment_features,
    build_pl_vector,
    build_v_vector,
    residual_match,
)

# ============================================================
# 1. Load data
# ============================================================

pl_feats = load_pl_channel_features()
per_ch = pl_feats['T5_channel_signatures']['per_chapter']
op_profiles = load_b_operational_profiles()
deploy_features, _ = load_b_deployment_features()

# ============================================================
# 2. Identify the target chapters
# ============================================================

# Higher Mercuriorum chapters with procedural content
# These are chapter_idx 162+ (Mercuriorum section) with chapter_number >= 36
# We want the procedural ones: Ch40M, Ch42M, Ch43M, Ch47M, Ch48M, Ch50M, Ch51M, Ch52M

# Mercuriorum chapters start at idx ~162 in the features file
# Need to identify them by both chapter_number AND being in the Mercuriorum range
merc_higher = {}
for ch in per_ch:
    idx = ch['chapter_idx']
    num = ch['chapter_number']
    # Mercuriorum higher chapters are idx 162-178
    if idx >= 162 and idx <= 178:
        merc_higher[idx] = ch

print("=" * 100)
print("FCH HARD-FILTER MATCHING: Higher Mercuriorum Chapters → Unmatched fch Folios")
print("=" * 100)

print("\nAll Mercuriorum chapters idx >= 162:")
for idx in sorted(merc_higher):
    ch = merc_higher[idx]
    print(f"  idx={idx:3d} Ch{ch['chapter_number']}M  fam={ch.get('family','?'):15s} "
          f"heat={ch['k_channel']['heat_rate']:.3f} mon={ch['h_channel']['monitoring_rate']:.3f} "
          f"corr={ch['e_channel']['correction_rate']:.3f} term={ch['t_channel']['termination_rate']:.3f}")

# Select procedural chapters (exclude Ch44M which is already matched, and theoretical-only chapters)
# Based on our reading:
# Ch40M (idx=166): silver transmutation — ~20 operational verbs
# Ch42M (idx=167): lead work — 14 verbs, family=fixation
# Ch43M (idx=168): tin work — 7 verbs, family=fixation
# Ch45M (idx=170): Venus/Mars (dissolution) — mixed, 9-10 verbs
# Ch47M (idx=173): coded elemental separation — 20+ verbs, family=separation
# Ch48M (idx=174): ferment preparation — 13 verbs, family=sublimation
# Ch50M (idx=176): error correction — 12 verbs, family=separation
# Ch51M (idx=177): "our vinegar" recipe — 8 verbs, family=dissolution
# Ch52M (idx=178): projection technique — 15 verbs, mixed

TARGET_CHAPTER_IDXS = [166, 167, 168, 173, 174, 176, 177, 178]  # Ch40,42,43,47,48,50,51,52
# Also include Ch45M dissolution entry (idx=170) as borderline procedural
TARGET_CHAPTER_IDXS_EXTENDED = TARGET_CHAPTER_IDXS + [170]

target_chapters = [merc_higher[idx] for idx in TARGET_CHAPTER_IDXS if idx in merc_higher]

print(f"\nTarget chapters (procedural, N={len(target_chapters)}):")
for ch in target_chapters:
    vec = build_pl_vector(ch, TUNED_DIMS)
    print(f"  Ch{ch['chapter_number']}M (idx={ch['chapter_idx']}) fam={ch.get('family','?'):15s} "
          f"8D=[{', '.join(f'{v:.3f}' for v in vec)}]")

# ============================================================
# 3. Identify the target folios
# ============================================================

# 7 unmatched folios with fch (mercury marker)
TARGET_FOLIOS = ['f40v', 'f50r', 'f86v3', 'f106v', 'f111r', 'f113r', 'f113v']

print(f"\nTarget folios (unmatched + fch, N={len(TARGET_FOLIOS)}):")
missing = []
for f in TARGET_FOLIOS:
    in_op = f in op_profiles
    in_dep = f in deploy_features
    vec = build_v_vector(f, op_profiles, deploy_features, TUNED_DIMS)
    has_data = any(v != 0.0 for v in vec)
    status = "OK" if has_data else "ZERO" if in_op else "MISSING"
    if not has_data:
        missing.append(f)
    print(f"  {f:8s} op={in_op} dep={in_dep} status={status} "
          f"8D=[{', '.join(f'{v:.3f}' for v in vec)}]")

if missing:
    print(f"\n  WARNING: {len(missing)} folios have no/zero features: {missing}")
    # Remove folios with no data
    TARGET_FOLIOS = [f for f in TARGET_FOLIOS if f not in missing]
    print(f"  Proceeding with {len(TARGET_FOLIOS)} folios")

# ============================================================
# 4. Run the 8D residual matching
# ============================================================

print("\n" + "=" * 100)
print("8D RESIDUAL MATCHING")
print("=" * 100)

# Use only folios that have data
if len(target_chapters) == 0 or len(TARGET_FOLIOS) == 0:
    print("ERROR: No chapters or folios to match!")
    sys.exit(1)

result = residual_match(
    pl_chapters=target_chapters,
    v_folios=TARGET_FOLIOS,
    dims=TUNED_DIMS,
    op_profiles=op_profiles,
    deploy_features=deploy_features,
)

print(f"\nMatching {len(target_chapters)} chapters → {len(TARGET_FOLIOS)} folios")
print(f"Mean distance: {result['mean_distance']:.3f}")
print(f"Mean ratio: {result['mean_ratio']:.3f}")
print(f"Confident (ratio > 1.15): {result['n_confident']}/{len(target_chapters)}")
print(f"Unique nearest-neighbor targets: {result['n_unique_nn']}")

DIM_NAMES = ['heat(-k)', 'monitor(h)', 'correct(e)', 'terminal',
             'consist(-m)', 'heat(-sfx)', 'monitor(-hdr)', 'thermo_ke']

print(f"\n{'Ch':>5s} {'Folio':>8s} {'Dist':>6s} {'Ratio':>6s} {'Conf':>5s} {'Family':>15s}  Per-dim contribution")
print("-" * 100)
for m in result['match_table']:
    dims_str = ' '.join(f"{d:.2f}" for d in m['per_dim_dist_sq'])
    conf = "YES" if m['confident'] else "no"
    print(f"  {m['chapter_number']:3d}M {m['folio']:>8s} {m['distance']:6.3f} {m['ratio']:6.3f} {conf:>5s} "
          f"{m['family']:>15s}  {dims_str}")

# ============================================================
# 5. Full distance matrix (for alternative assignments)
# ============================================================

print("\n" + "=" * 100)
print("FULL DISTANCE MATRIX")
print("=" * 100)

dmat = result['dmat']
# Print header
header = f"{'Ch':>5s} |"
for f in TARGET_FOLIOS:
    header += f" {f:>7s}"
print(header)
print("-" * (8 + 8 * len(TARGET_FOLIOS)))

for i, ch in enumerate(target_chapters):
    row = f"  {ch['chapter_number']:3d}M |"
    best_j = min(range(len(TARGET_FOLIOS)), key=lambda j: dmat[i][j])
    for j in range(len(TARGET_FOLIOS)):
        marker = " *" if j == best_j else "  "
        row += f" {dmat[i][j]:5.2f}{marker}"
    print(row)

print("\n  * = nearest neighbor (before greedy assignment)")

# ============================================================
# 6. Compare to existing matched chapters for context
# ============================================================

print("\n" + "=" * 100)
print("CONTEXT: How do these distances compare to existing confirmed matches?")
print("=" * 100)

# Load ALL PL chapters and run a broader comparison
# Get the original distillation chapters that were matched in Phase 628
CONFIRMED_MATCHES = {
    'f75r': 19,   # Ch19M aqua vitae
    'f76r': 18,   # Ch18P element separation  (Practica numbering differs)
    'f84r': 14,   # Ch14P gold dissolution
}

# Get the existing matched chapters for comparison
# Find Ch19M, Ch12M etc in the Mercuriorum section
merc_all = {ch['chapter_idx']: ch for ch in per_ch if ch['chapter_idx'] >= 126 and ch['chapter_idx'] <= 178}

# Show Phase 628 match distances for calibration
print("\nPhase 628 confirmed match distances (for calibration):")
for folio, ch_num in CONFIRMED_MATCHES.items():
    # Find this chapter in merc_all
    for idx, ch in merc_all.items():
        if ch['chapter_number'] == ch_num:
            v_vec = build_v_vector(folio, op_profiles, deploy_features, TUNED_DIMS)
            pl_vec = build_pl_vector(ch, TUNED_DIMS)
            # Apply signs
            for d, (_, _, sign) in enumerate(TUNED_DIMS):
                pl_vec[d] *= sign
            # Raw Euclidean (before centering/standardization — just for scale reference)
            raw_dist = math.sqrt(sum((pl_vec[d] - v_vec[d])**2 for d in range(8)))
            print(f"  {folio} ↔ Ch{ch_num}M: raw_dist={raw_dist:.3f}")
            break

# ============================================================
# 7. Summary and recommendations
# ============================================================

print("\n" + "=" * 100)
print("SUMMARY & RECOMMENDATIONS")
print("=" * 100)

ch_names = {
    40: "Silver transmutation (dissolve, whiten, sublimate, project)",
    42: "Lead work (separate, purify, sublimate, incerate, project)",
    43: "Tin work (sublimate, incerate, project — refs Ch42)",
    47: "Coded elemental separation (ABC cipher, 4 elements)",
    48: "Ferment preparation + multiplication ratios",
    50: "Error correction / troubleshooting",
    51: "Our vinegar recipe (constrain quicksilver)",
    52: "Projection technique (simple + conversion)",
}

for m in sorted(result['match_table'], key=lambda x: x['distance']):
    ch_num = m['chapter_number']
    desc = ch_names.get(ch_num, '?')
    conf = "CONFIDENT" if m['confident'] else "tentative"
    print(f"\n  Ch{ch_num}M → {m['folio']} (d={m['distance']:.3f}, ratio={m['ratio']:.3f}, {conf})")
    print(f"    Recipe: {desc}")

    # Show which dimensions drive the match
    top_dims = sorted(range(8), key=lambda d: m['per_dim_dist_sq'][d])
    best_dim = DIM_NAMES[top_dims[0]]
    worst_dim = DIM_NAMES[top_dims[-1]]
    print(f"    Best alignment: {best_dim} (sq={m['per_dim_dist_sq'][top_dims[0]]:.3f})")
    print(f"    Worst alignment: {worst_dim} (sq={m['per_dim_dist_sq'][top_dims[-1]]:.3f})")

# Save results
output = {
    'match_table': result['match_table'],
    'mean_distance': result['mean_distance'],
    'mean_ratio': result['mean_ratio'],
    'n_confident': result['n_confident'],
    'target_chapters': [f"Ch{merc_higher[idx]['chapter_number']}M" for idx in TARGET_CHAPTER_IDXS if idx in merc_higher],
    'target_folios': TARGET_FOLIOS,
}
out_path = 'C:/git/voynich/phases/RECIPE_FOLIO_CORRESPONDENCE/results/fch_hard_filter_matching.json'
with open(out_path, 'w') as f:
    json.dump(output, f, indent=2)
print(f"\n\nResults saved to {out_path}")
