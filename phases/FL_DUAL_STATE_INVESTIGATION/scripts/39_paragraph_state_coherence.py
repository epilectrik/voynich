"""
39_paragraph_state_coherence.py

Do paragraph boundaries correspond to state-grid neighborhoods?

If the folio is a lookup table covering a region of the (action, oversight)
grid, what role does the paragraph play? Three hypotheses:

  H1: PARAGRAPH = STATE CLUSTER — lines within a paragraph cluster around
      a specific state neighborhood (within-para distance < between-para)
  H2: PARAGRAPH = MINI-SWEEP — each paragraph sweeps its own sub-region
      of the folio's grid patch (paragraph centroids spread apart)
  H3: PARAGRAPH = STRUCTURAL ONLY — paragraph boundaries don't align with
      state coordinates (random partitioning of the grid patch)

Tests:
  1. Within-paragraph vs between-paragraph state distance (permutation test)
  2. Paragraph centroid spread (do centroids partition the grid?)
  3. Header line coordinate vs body lines (does the header set the state?)
  4. Paragraph diameter (how wide is each paragraph's state coverage?)
  5. Paragraph execution gradient (does state shift spec→exec within para?)
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np
from sklearn.mixture import GaussianMixture
from scipy.stats import mannwhitneyu, spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

FL_STAGE_MAP = {
    'ii': ('INITIAL', 0.299), 'i': ('INITIAL', 0.345),
    'in': ('EARLY', 0.421),
    'r': ('MEDIAL', 0.507), 'ar': ('MEDIAL', 0.545),
    'al': ('LATE', 0.606), 'l': ('LATE', 0.618), 'ol': ('LATE', 0.643),
    'o': ('FINAL', 0.751), 'ly': ('FINAL', 0.785), 'am': ('FINAL', 0.802),
    'm': ('TERMINAL', 0.861), 'dy': ('TERMINAL', 0.908),
    'ry': ('TERMINAL', 0.913), 'y': ('TERMINAL', 0.942),
}
STAGE_ORDER = {'INITIAL': 0, 'EARLY': 1, 'MEDIAL': 2, 'LATE': 3, 'FINAL': 4, 'TERMINAL': 5}
STAGES = ['INITIAL', 'EARLY', 'MEDIAL', 'LATE', 'FINAL', 'TERMINAL']

tx = Transcript()
morph = Morphology()
MIN_N = 50

# ============================================================
# Build line data with paragraph membership
# ============================================================
line_tokens = defaultdict(list)
line_meta = {}
folio_lines_ordered = defaultdict(list)

for t in tx.currier_b():
    key = (t.folio, t.line)
    line_tokens[key].append(t)
    if key not in line_meta:
        line_meta[key] = {
            'section': t.section, 'folio': t.folio,
            'par_initial': False, 'par_final': False,
        }
        folio_lines_ordered[t.folio].append(key)
    if t.par_initial:
        line_meta[key]['par_initial'] = True
    if t.par_final:
        line_meta[key]['par_final'] = True

# Deduplicate
for f in folio_lines_ordered:
    seen = set()
    deduped = []
    for k in folio_lines_ordered[f]:
        if k not in seen:
            seen.add(k)
            deduped.append(k)
    folio_lines_ordered[f] = deduped

# ============================================================
# Build paragraphs per folio
# ============================================================
folio_paragraphs = defaultdict(list)  # folio -> list of [line_key, ...]

for folio, keys in folio_lines_ordered.items():
    current_para = []
    for key in keys:
        meta = line_meta[key]
        if meta['par_initial'] and current_para:
            folio_paragraphs[folio].append(current_para)
            current_para = []
        current_para.append(key)
        if meta['par_final']:
            folio_paragraphs[folio].append(current_para)
            current_para = []
    if current_para:
        folio_paragraphs[folio].append(current_para)

# ============================================================
# Fit GMMs and assign coordinates
# ============================================================
per_middle_positions = defaultdict(list)
for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n <= 1:
        continue
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        if m and m.middle and m.middle in FL_STAGE_MAP:
            per_middle_positions[m.middle].append(idx / (n - 1))

gmm_models = {}
for mid, positions in per_middle_positions.items():
    if len(positions) < MIN_N:
        continue
    X = np.array(positions).reshape(-1, 1)
    gmm = GaussianMixture(n_components=2, random_state=42, n_init=10)
    gmm.fit(X)
    if gmm.means_[0] > gmm.means_[1]:
        gmm_models[mid] = {'model': gmm, 'swap': True}
    else:
        gmm_models[mid] = {'model': gmm, 'swap': False}

line_coords = {}
for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n < 6:
        continue
    fl_info = []
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        pos = idx / (n - 1) if n > 1 else 0.5
        mid = m.middle if m else None
        is_fl = mid is not None and mid in FL_STAGE_MAP
        if is_fl and mid in gmm_models:
            info = gmm_models[mid]
            pred = info['model'].predict(np.array([[pos]]))[0]
            if info['swap']:
                pred = 1 - pred
            mode = 'LOW' if pred == 0 else 'HIGH'
            stage = FL_STAGE_MAP[mid][0]
            fl_info.append({'mode': mode, 'stage': stage})

    low_fls = [f for f in fl_info if f['mode'] == 'LOW']
    high_fls = [f for f in fl_info if f['mode'] == 'HIGH']
    if not low_fls or not high_fls:
        continue
    low_stage = Counter(f['stage'] for f in low_fls).most_common(1)[0][0]
    high_stage = Counter(f['stage'] for f in high_fls).most_common(1)[0][0]
    line_coords[line_key] = {
        'low': low_stage, 'high': high_stage,
        'lo': STAGE_ORDER[low_stage], 'ho': STAGE_ORDER[high_stage],
    }

print(f"Lines with coordinates: {len(line_coords)}")

# ============================================================
# 1. WITHIN-PARAGRAPH vs BETWEEN-PARAGRAPH STATE DISTANCE
# ============================================================
print(f"\n{'='*70}")
print("1. WITHIN-PARAGRAPH vs BETWEEN-PARAGRAPH STATE DISTANCE")
print("=" * 70)

within_dists = []
between_dists = []

for folio, paras in folio_paragraphs.items():
    # Get coordinated lines per paragraph
    para_coords_list = []
    for para in paras:
        coords = [(line_coords[k]['lo'], line_coords[k]['ho']) for k in para if k in line_coords]
        if len(coords) >= 2:
            para_coords_list.append(coords)

    if len(para_coords_list) < 2:
        continue

    # Within-paragraph distances
    for coords in para_coords_list:
        for i in range(len(coords)):
            for j in range(i + 1, len(coords)):
                d = abs(coords[i][0] - coords[j][0]) + abs(coords[i][1] - coords[j][1])
                within_dists.append(d)

    # Between-paragraph distances (all pairs from different paragraphs)
    for pi in range(len(para_coords_list)):
        for pj in range(pi + 1, len(para_coords_list)):
            for ci in para_coords_list[pi]:
                for cj in para_coords_list[pj]:
                    d = abs(ci[0] - cj[0]) + abs(ci[1] - cj[1])
                    between_dists.append(d)

mean_within = np.mean(within_dists)
mean_between = np.mean(between_dists)
ratio = mean_within / mean_between if mean_between > 0 else 0

print(f"\n  Within-paragraph mean distance:  {mean_within:.3f}")
print(f"  Between-paragraph mean distance: {mean_between:.3f}")
print(f"  Ratio (within/between):          {ratio:.3f}")
print(f"  N within pairs: {len(within_dists)}, N between pairs: {len(between_dists)}")

if within_dists and between_dists:
    u_stat, p_wb = mannwhitneyu(within_dists, between_dists, alternative='less')
    cohens_d = (mean_between - mean_within) / np.sqrt((np.var(within_dists) + np.var(between_dists)) / 2)
    print(f"  Mann-Whitney U (within < between): U={u_stat:.0f}, p={p_wb:.6f}")
    print(f"  Cohen's d: {cohens_d:.3f}")
else:
    p_wb = 1.0
    cohens_d = 0.0

# Permutation test: shuffle paragraph labels within each folio
n_perm = 1000
perm_ratios = []
rng = np.random.default_rng(42)

for _ in range(n_perm):
    perm_within = []
    perm_between = []
    for folio, paras in folio_paragraphs.items():
        # Get all coordinated lines in this folio
        all_coords = []
        para_sizes = []
        for para in paras:
            coords = [(line_coords[k]['lo'], line_coords[k]['ho']) for k in para if k in line_coords]
            if len(coords) >= 2:
                all_coords.extend(coords)
                para_sizes.append(len(coords))

        if len(para_sizes) < 2:
            continue

        # Shuffle and re-assign to fake paragraphs of same sizes
        shuffled = list(range(len(all_coords)))
        rng.shuffle(shuffled)
        fake_paras = []
        idx = 0
        for sz in para_sizes:
            fake_paras.append([all_coords[shuffled[k]] for k in range(idx, idx + sz)])
            idx += sz

        for coords in fake_paras:
            for i in range(len(coords)):
                for j in range(i + 1, len(coords)):
                    d = abs(coords[i][0] - coords[j][0]) + abs(coords[i][1] - coords[j][1])
                    perm_within.append(d)

        for pi in range(len(fake_paras)):
            for pj in range(pi + 1, len(fake_paras)):
                for ci in fake_paras[pi]:
                    for cj in fake_paras[pj]:
                        d = abs(ci[0] - cj[0]) + abs(ci[1] - cj[1])
                        perm_between.append(d)

    if perm_between:
        perm_ratios.append(np.mean(perm_within) / np.mean(perm_between))

actual_ratio = ratio
if perm_ratios:
    perm_p = np.mean([r <= actual_ratio for r in perm_ratios])
    print(f"\n  Permutation test (1000 shuffles):")
    print(f"    Actual ratio: {actual_ratio:.4f}")
    print(f"    Permuted mean ratio: {np.mean(perm_ratios):.4f}")
    print(f"    p (actual <= permuted): {perm_p:.4f}")
else:
    perm_p = 1.0

pass_1 = p_wb < 0.01 and cohens_d > 0.2
print(f"\n  CHECK 1 (within < between): {'PASS' if pass_1 else 'FAIL'} "
      f"(p={p_wb:.6f}, d={cohens_d:.3f})")

# ============================================================
# 2. PARAGRAPH CENTROID SPREAD
# ============================================================
print(f"\n{'='*70}")
print("2. PARAGRAPH CENTROID SPREAD")
print("=" * 70)

folio_centroid_spreads = []
folio_centroid_data = []

for folio, paras in folio_paragraphs.items():
    centroids = []
    for para in paras:
        coords = [(line_coords[k]['lo'], line_coords[k]['ho']) for k in para if k in line_coords]
        if len(coords) >= 2:
            lo_mean = np.mean([c[0] for c in coords])
            ho_mean = np.mean([c[1] for c in coords])
            centroids.append((lo_mean, ho_mean))

    if len(centroids) < 2:
        continue

    # Mean pairwise centroid distance
    cent_dists = []
    for i in range(len(centroids)):
        for j in range(i + 1, len(centroids)):
            d = abs(centroids[i][0] - centroids[j][0]) + abs(centroids[i][1] - centroids[j][1])
            cent_dists.append(d)

    mean_spread = np.mean(cent_dists)
    folio_centroid_spreads.append(mean_spread)
    folio_centroid_data.append({
        'folio': folio,
        'n_paras': len(centroids),
        'centroids': [(round(c[0], 2), round(c[1], 2)) for c in centroids],
        'mean_spread': round(mean_spread, 3),
    })

mean_centroid_spread = np.mean(folio_centroid_spreads) if folio_centroid_spreads else 0
print(f"\n  Folios with 2+ coordinated paragraphs: {len(folio_centroid_spreads)}")
print(f"  Mean centroid pairwise distance: {mean_centroid_spread:.3f}")
print(f"  Std: {np.std(folio_centroid_spreads):.3f}")

# Compare centroid spread to random expectation
# If centroids are spread apart, paragraphs partition the grid
# If centroids are close together, paragraphs share the same neighborhood
if folio_centroid_spreads:
    low_spread = np.mean([s < 1.0 for s in folio_centroid_spreads])
    high_spread = np.mean([s > 2.0 for s in folio_centroid_spreads])
    print(f"  Tight centroids (spread < 1.0): {low_spread*100:.1f}%")
    print(f"  Spread centroids (spread > 2.0): {high_spread*100:.1f}%")

pass_2 = mean_centroid_spread > 1.5  # centroids meaningfully apart
print(f"\n  CHECK 2 (centroids spread): {'PASS' if pass_2 else 'FAIL'} "
      f"(mean spread={mean_centroid_spread:.3f})")

# ============================================================
# 3. HEADER LINE vs BODY LINES
# ============================================================
print(f"\n{'='*70}")
print("3. HEADER LINE (LINE 1) vs BODY LINES")
print("=" * 70)

header_matches = 0
header_total = 0
header_body_dists = []

for folio, paras in folio_paragraphs.items():
    for para in paras:
        if len(para) < 2:
            continue
        coordinated = [(k, line_coords[k]) for k in para if k in line_coords]
        if len(coordinated) < 2:
            continue

        # Header = first coordinated line, body = rest
        _, header_coord = coordinated[0]
        body_coords = [c for _, c in coordinated[1:]]

        # Does header state match majority body state?
        body_states = [(c['lo'], c['ho']) for c in body_coords]
        header_state = (header_coord['lo'], header_coord['ho'])

        # Modal body state
        modal_body = Counter(body_states).most_common(1)[0][0]
        if header_state == modal_body:
            header_matches += 1
        header_total += 1

        # Mean distance from header to body
        for bc in body_coords:
            d = abs(header_coord['lo'] - bc['lo']) + abs(header_coord['ho'] - bc['ho'])
            header_body_dists.append(d)

if header_total > 0:
    header_match_rate = header_matches / header_total
    mean_hb_dist = np.mean(header_body_dists)
    print(f"\n  Paragraphs with coordinated header+body: {header_total}")
    print(f"  Header matches modal body state: {header_matches}/{header_total} ({header_match_rate*100:.1f}%)")
    print(f"  Mean header-to-body distance: {mean_hb_dist:.3f}")

    # Compare to within-body distances
    within_body_dists = []
    for folio, paras in folio_paragraphs.items():
        for para in paras:
            coordinated = [(k, line_coords[k]) for k in para if k in line_coords]
            if len(coordinated) < 3:
                continue
            body_coords = [c for _, c in coordinated[1:]]
            for i in range(len(body_coords)):
                for j in range(i + 1, len(body_coords)):
                    d = abs(body_coords[i]['lo'] - body_coords[j]['lo']) + \
                        abs(body_coords[i]['ho'] - body_coords[j]['ho'])
                    within_body_dists.append(d)

    if within_body_dists:
        mean_body_dist = np.mean(within_body_dists)
        print(f"  Mean within-body distance: {mean_body_dist:.3f}")
        print(f"  Header-body / within-body: {mean_hb_dist / mean_body_dist:.3f}" if mean_body_dist > 0 else "")
else:
    header_match_rate = 0
    mean_hb_dist = 0
    mean_body_dist = 0

pass_3 = header_match_rate > 0.25  # header matches body state >25% of the time
print(f"\n  CHECK 3 (header sets state): {'PASS' if pass_3 else 'FAIL'} "
      f"(match rate={header_match_rate*100:.1f}%)")

# ============================================================
# 4. PARAGRAPH STATE DIAMETER
# ============================================================
print(f"\n{'='*70}")
print("4. PARAGRAPH STATE DIAMETER")
print("=" * 70)

para_diameters = []
para_unique_counts = []

for folio, paras in folio_paragraphs.items():
    for para in paras:
        coords = [(line_coords[k]['lo'], line_coords[k]['ho']) for k in para if k in line_coords]
        if len(coords) < 2:
            continue

        unique_states = list(set(coords))
        para_unique_counts.append(len(unique_states))

        # Diameter = max pairwise Manhattan distance
        max_d = 0
        for i in range(len(unique_states)):
            for j in range(i + 1, len(unique_states)):
                d = abs(unique_states[i][0] - unique_states[j][0]) + \
                    abs(unique_states[i][1] - unique_states[j][1])
                if d > max_d:
                    max_d = d
        para_diameters.append(max_d)

if para_diameters:
    mean_diameter = np.mean(para_diameters)
    mean_unique = np.mean(para_unique_counts)
    print(f"\n  Paragraphs with 2+ coordinated lines: {len(para_diameters)}")
    print(f"  Mean unique states per paragraph: {mean_unique:.1f}")
    print(f"  Mean state diameter: {mean_diameter:.2f}")
    print(f"  Diameter distribution:")
    for d_val in range(0, 11):
        count = sum(1 for d in para_diameters if d == d_val)
        if count > 0:
            pct = count / len(para_diameters) * 100
            print(f"    Diameter {d_val}: {count:>4} ({pct:.1f}%)")

    tight_paras = sum(1 for d in para_diameters if d <= 2)
    wide_paras = sum(1 for d in para_diameters if d >= 5)
    tight_pct = tight_paras / len(para_diameters) * 100
    wide_pct = wide_paras / len(para_diameters) * 100
    print(f"\n  TIGHT (diameter <= 2): {tight_paras} ({tight_pct:.1f}%)")
    print(f"  WIDE  (diameter >= 5): {wide_paras} ({wide_pct:.1f}%)")
else:
    mean_diameter = 0
    tight_pct = 0
    wide_pct = 0

pass_4 = tight_pct > 40  # >40% of paragraphs are state-tight
print(f"\n  CHECK 4 (tight paragraphs): {'PASS' if pass_4 else 'FAIL'} "
      f"(tight={tight_pct:.1f}%)")

# ============================================================
# 5. EXECUTION GRADIENT WITHIN PARAGRAPHS
# ============================================================
print(f"\n{'='*70}")
print("5. EXECUTION GRADIENT WITHIN PARAGRAPHS")
print("=" * 70)

# Does state shift systematically from spec→exec within a paragraph?
# For paragraphs with 4+ lines: correlate line position with state ordinal

para_lo_rhos = []
para_ho_rhos = []

for folio, paras in folio_paragraphs.items():
    for para in paras:
        coordinated = [(i, line_coords[k]) for i, k in enumerate(para) if k in line_coords]
        if len(coordinated) < 4:
            continue

        positions = [c[0] for c in coordinated]
        lo_vals = [c[1]['lo'] for c in coordinated]
        ho_vals = [c[1]['ho'] for c in coordinated]

        if len(set(lo_vals)) > 1:
            rho_lo, _ = spearmanr(positions, lo_vals)
            para_lo_rhos.append(rho_lo)
        if len(set(ho_vals)) > 1:
            rho_ho, _ = spearmanr(positions, ho_vals)
            para_ho_rhos.append(rho_ho)

if para_lo_rhos:
    mean_rho_lo = np.mean(para_lo_rhos)
    mean_rho_ho = np.mean(para_ho_rhos)
    print(f"\n  Paragraphs with 4+ coordinated lines: {len(para_lo_rhos)}")
    print(f"  Mean rho (line position -> ACTION):    {mean_rho_lo:+.3f}")
    print(f"  Mean rho (line position -> OVERSIGHT):  {mean_rho_ho:+.3f}")

    # Distribution of rho
    for label, rhos in [("ACTION", para_lo_rhos), ("OVERSIGHT", para_ho_rhos)]:
        neg = sum(1 for r in rhos if r < -0.3)
        flat = sum(1 for r in rhos if -0.3 <= r <= 0.3)
        pos = sum(1 for r in rhos if r > 0.3)
        print(f"  {label}: {neg} decreasing, {flat} flat, {pos} increasing")
else:
    mean_rho_lo = 0
    mean_rho_ho = 0

pass_5 = abs(mean_rho_lo) > 0.15 or abs(mean_rho_ho) > 0.15
print(f"\n  CHECK 5 (execution gradient): {'PASS' if pass_5 else 'FAIL'} "
      f"(rho_lo={mean_rho_lo:+.3f}, rho_ho={mean_rho_ho:+.3f})")

# ============================================================
# 6. EXAMPLE PARAGRAPHS
# ============================================================
print(f"\n{'='*70}")
print("6. EXAMPLE PARAGRAPHS (tightest and widest)")
print("=" * 70)

# Find a few tight and wide examples
para_examples = []
for folio, paras in folio_paragraphs.items():
    for pi, para in enumerate(paras):
        coords = [(k, line_coords[k]) for k in para if k in line_coords]
        if len(coords) < 2:
            continue
        states = [(c['lo'], c['ho']) for _, c in coords]
        unique_states = list(set(states))
        max_d = 0
        for i in range(len(unique_states)):
            for j in range(i + 1, len(unique_states)):
                d = abs(unique_states[i][0] - unique_states[j][0]) + \
                    abs(unique_states[i][1] - unique_states[j][1])
                if d > max_d:
                    max_d = d
        centroid = (np.mean([s[0] for s in states]), np.mean([s[1] for s in states]))
        para_examples.append({
            'folio': folio,
            'para_idx': pi + 1,
            'n_lines': len(coords),
            'diameter': max_d,
            'unique_states': len(unique_states),
            'centroid': (round(centroid[0], 2), round(centroid[1], 2)),
            'states': [(STAGES[s[0]], STAGES[s[1]]) for s in states],
            'section': line_meta[para[0]]['section'],
        })

# Sort by diameter
para_examples.sort(key=lambda x: x['diameter'])

print("\n  TIGHT examples (diameter <= 1):")
shown = 0
for ex in para_examples:
    if ex['diameter'] <= 1 and ex['n_lines'] >= 3 and shown < 5:
        state_str = ', '.join(f"({s[0][:4]},{s[1][:4]})" for s in ex['states'])
        print(f"    {ex['folio']} P{ex['para_idx']} ({ex['section']}): "
              f"{ex['n_lines']} lines, diameter={ex['diameter']}, "
              f"states=[{state_str}]")
        shown += 1

print("\n  WIDE examples (diameter >= 6):")
shown = 0
for ex in reversed(para_examples):
    if ex['diameter'] >= 6 and shown < 5:
        state_str = ', '.join(f"({s[0][:4]},{s[1][:4]})" for s in ex['states'])
        print(f"    {ex['folio']} P{ex['para_idx']} ({ex['section']}): "
              f"{ex['n_lines']} lines, diameter={ex['diameter']}, "
              f"unique={ex['unique_states']}, centroid={ex['centroid']}")
        shown += 1

# ============================================================
# 7. VERDICT
# ============================================================
print(f"\n{'='*70}")
print("7. VERDICT")
print("=" * 70)

checks = [pass_1, pass_2, pass_3, pass_4, pass_5]
n_pass = sum(checks)

if pass_1 and pass_4 and not pass_5:
    verdict = "STATE_CLUSTER"
    explanation = ("Paragraphs cluster around state neighborhoods "
                   "(within < between, tight diameters) but no execution gradient")
elif pass_1 and pass_2 and pass_5:
    verdict = "MINI_SWEEP"
    explanation = ("Paragraphs sweep sub-regions with centroids spread apart "
                   "and an internal gradient")
elif pass_5 and not pass_1:
    verdict = "GRADIENT_ONLY"
    explanation = ("State shifts within paragraphs (execution gradient) "
                   "but no clustering effect")
elif n_pass <= 1:
    verdict = "STRUCTURAL_ONLY"
    explanation = ("Paragraph boundaries don't align with state coordinates - "
                   "paragraphs partition structure, not state")
else:
    verdict = "PARTIAL_ALIGNMENT"
    explanation = f"{n_pass}/5 checks pass - paragraphs weakly align with state neighborhoods"

print(f"\n  Checks passed: {n_pass}/5")
print(f"  1. Within < between distance: {'PASS' if pass_1 else 'FAIL'}")
print(f"  2. Centroids spread:          {'PASS' if pass_2 else 'FAIL'}")
print(f"  3. Header sets state:         {'PASS' if pass_3 else 'FAIL'}")
print(f"  4. Tight paragraphs:          {'PASS' if pass_4 else 'FAIL'}")
print(f"  5. Execution gradient:        {'PASS' if pass_5 else 'FAIL'}")
print(f"\n  VERDICT: {verdict}")
print(f"  {explanation}")

# ============================================================
# Write results
# ============================================================
results = {
    'within_vs_between': {
        'mean_within': round(float(mean_within), 3),
        'mean_between': round(float(mean_between), 3),
        'ratio': round(float(ratio), 4),
        'p_mannwhitney': round(float(p_wb), 6),
        'cohens_d': round(float(cohens_d), 3),
        'p_permutation': round(float(perm_p), 4),
        'pass': bool(pass_1),
    },
    'centroid_spread': {
        'mean_spread': round(float(mean_centroid_spread), 3),
        'n_folios': len(folio_centroid_spreads),
        'pass': bool(pass_2),
    },
    'header_body': {
        'match_rate': round(float(header_match_rate), 3) if header_total > 0 else None,
        'mean_header_body_dist': round(float(mean_hb_dist), 3) if header_body_dists else None,
        'n_paragraphs': header_total,
        'pass': bool(pass_3),
    },
    'paragraph_diameter': {
        'mean_diameter': round(float(mean_diameter), 2),
        'mean_unique_states': round(float(mean_unique), 1) if para_unique_counts else None,
        'tight_pct': round(float(tight_pct), 1),
        'wide_pct': round(float(wide_pct), 1) if para_diameters else None,
        'n_paragraphs': len(para_diameters),
        'pass': bool(pass_4),
    },
    'execution_gradient': {
        'mean_rho_action': round(float(mean_rho_lo), 3) if para_lo_rhos else None,
        'mean_rho_oversight': round(float(mean_rho_ho), 3) if para_ho_rhos else None,
        'n_paragraphs': len(para_lo_rhos),
        'pass': bool(pass_5),
    },
    'verdict': verdict,
    'explanation': explanation,
    'checks_passed': n_pass,
}

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

out_path = Path(__file__).resolve().parent.parent / 'results' / '39_paragraph_state_coherence.json'
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2, cls=NpEncoder)
print(f"\nResult written to {out_path}")
