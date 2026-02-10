"""
30_operator_navigation.py

How would an operator actually USE this manuscript?

Test the lookup model: given a material state (FL pair),
which folio(s) contain instructions for that state?

Questions:
  1. Do folios specialize in certain FL pair regions?
  2. How many folios does each pair appear in? (1 = dedicated, many = distributed)
  3. Given a pair, how many folios are candidates? (navigation precision)
  4. Do sections partition the grid? (section = process type?)
  5. Is there a folio-level "address" visible from FL pairs?
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np
from sklearn.mixture import GaussianMixture
from scipy.stats import chi2_contingency

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

class_map_path = Path(__file__).resolve().parents[3] / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_role = class_data['token_to_role']

line_tokens = defaultdict(list)
line_sections = {}
for t in tx.currier_b():
    key = (t.folio, t.line)
    line_tokens[key].append(t)
    line_sections[key] = t.section

# Fit GMMs
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

# ============================================================
# Assign FL pairs to lines
# ============================================================
line_pairs = {}  # line_key -> pair
folio_pairs = defaultdict(list)  # folio -> [pairs]
folio_sections = {}

for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n < 4:
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

    if low_fls and high_fls:
        low_stage = Counter(f['stage'] for f in low_fls).most_common(1)[0][0]
        high_stage = Counter(f['stage'] for f in high_fls).most_common(1)[0][0]
        pair = (low_stage, high_stage)
        line_pairs[line_key] = pair
        folio_pairs[line_key[0]].append(pair)
        folio_sections[line_key[0]] = line_sections[line_key]

print(f"Lines with FL pairs: {len(line_pairs)}")
print(f"Folios with FL pairs: {len(folio_pairs)}")

# ============================================================
# TEST 1: How many unique pairs per folio?
# ============================================================
print(f"\n{'='*60}")
print("TEST 1: FL PAIR DIVERSITY PER FOLIO")
print(f"{'='*60}")

folio_diversity = []
folio_top_pair_coverage = []
for folio, pairs in folio_pairs.items():
    if len(pairs) < 5:
        continue
    unique = len(set(pairs))
    total = len(pairs)
    diversity = unique / total
    folio_diversity.append(diversity)

    top_pair = Counter(pairs).most_common(1)[0]
    top_coverage = top_pair[1] / total
    folio_top_pair_coverage.append(top_coverage)

print(f"  Mean unique pairs / total lines: {np.mean(folio_diversity):.3f}")
print(f"  Median: {np.median(folio_diversity):.3f}")
print(f"  Mean top-pair coverage: {np.mean(folio_top_pair_coverage):.1%}")
print(f"  Folios where top pair > 30%: "
      f"{sum(1 for c in folio_top_pair_coverage if c > 0.30)}/{len(folio_top_pair_coverage)}")

# Show some examples
print(f"\n  Example folios:")
for folio in sorted(folio_pairs.keys())[:15]:
    pairs = folio_pairs[folio]
    if len(pairs) < 5:
        continue
    pair_counts = Counter(pairs)
    total = len(pairs)
    unique = len(set(pairs))
    top3 = pair_counts.most_common(3)
    section = folio_sections.get(folio, '?')
    top3_str = ', '.join(f"{p[0][:4]}>{p[1][:4]}({c})" for p, c in top3)
    print(f"    {folio} (S={section}, n={total}, uniq={unique}): {top3_str}")

# ============================================================
# TEST 2: How many folios per pair?
# ============================================================
print(f"\n{'='*60}")
print("TEST 2: FOLIO SPREAD PER FL PAIR")
print(f"{'='*60}")

pair_folios = defaultdict(set)
pair_total_lines = Counter()
for line_key, pair in line_pairs.items():
    pair_folios[pair].add(line_key[0])
    pair_total_lines[pair] += 1

common_pairs = [(p, len(fs)) for p, fs in pair_folios.items()
                if pair_total_lines[p] >= 10]
common_pairs.sort(key=lambda x: -x[1])

print(f"\n  {'Pair':>12} {'Lines':>6} {'Folios':>7} {'Lines/Folio':>12} {'Concentrated?':>14}")
print(f"  {'-'*55}")

concentrated_pairs = 0
for pair, n_folios in common_pairs:
    n_lines = pair_total_lines[pair]
    lines_per_folio = n_lines / n_folios
    concentrated = lines_per_folio > 3.0
    if concentrated:
        concentrated_pairs += 1
    label = f"{pair[0][:4]}>{pair[1][:4]}"
    print(f"  {label:>12} {n_lines:>6} {n_folios:>7} {lines_per_folio:>12.1f} "
          f"{'YES' if concentrated else 'no':>14}")

print(f"\n  Concentrated pairs (>3 lines/folio): {concentrated_pairs}/{len(common_pairs)}")

# ============================================================
# TEST 3: Section partitioning of the grid
# ============================================================
print(f"\n{'='*60}")
print("TEST 3: SECTION PARTITIONING OF THE GRID")
print(f"{'='*60}")

# For each pair, what sections does it appear in?
pair_section_counts = defaultdict(Counter)
for line_key, pair in line_pairs.items():
    section = line_sections.get(line_key, '?')
    pair_section_counts[pair][section] += 1

print(f"\n  {'Pair':>12} {'n':>5}  {'B%':>5} {'S%':>5} {'H%':>5}  Dominant")
print(f"  {'-'*45}")

for pair in sorted(pair_section_counts.keys(),
                    key=lambda p: (STAGE_ORDER[p[0]], STAGE_ORDER[p[1]])):
    sections = pair_section_counts[pair]
    total = sum(sections.values())
    if total < 10:
        continue
    b_pct = sections.get('B', 0) / total * 100
    s_pct = sections.get('S', 0) / total * 100
    h_pct = sections.get('H', 0) / total * 100

    dominant = '-'
    if b_pct > 50:
        dominant = 'B'
    elif s_pct > 50:
        dominant = 'S'
    elif h_pct > 40:
        dominant = 'H'

    label = f"{pair[0][:4]}>{pair[1][:4]}"
    print(f"  {label:>12} {total:>5}  {b_pct:>4.0f}% {s_pct:>4.0f}% {h_pct:>4.0f}%  {dominant}")

# Overall section baseline
all_sections = Counter()
for line_key in line_pairs:
    all_sections[line_sections.get(line_key, '?')] += 1
total_all = sum(all_sections.values())
print(f"\n  Baseline: B={all_sections.get('B',0)/total_all*100:.0f}%, "
      f"S={all_sections.get('S',0)/total_all*100:.0f}%, "
      f"H={all_sections.get('H',0)/total_all*100:.0f}%")

# ============================================================
# TEST 4: Navigation precision
# ============================================================
print(f"\n{'='*60}")
print("TEST 4: NAVIGATION PRECISION")
print(f"{'='*60}")
print("  If you know the FL pair, how many candidate folios?")

# For each pair, compute: how many folios, and does adding
# section knowledge narrow it?
for pair in sorted(pair_section_counts.keys(),
                    key=lambda p: (STAGE_ORDER[p[0]], STAGE_ORDER[p[1]])):
    if pair_total_lines[pair] < 10:
        continue
    n_folios = len(pair_folios[pair])
    # If you also know the section, how many folios?
    pair_folio_sections = defaultdict(set)
    for line_key in line_pairs:
        if line_pairs[line_key] == pair:
            s = line_sections.get(line_key, '?')
            pair_folio_sections[s].add(line_key[0])

    best_section_folios = min(len(fs) for fs in pair_folio_sections.values()) if pair_folio_sections else n_folios

    label = f"{pair[0][:4]}>{pair[1][:4]}"
    print(f"  {label:>12}: {n_folios} folios total, "
          f"{best_section_folios} in best section")

# ============================================================
# TEST 5: Folio pair profile clustering
# ============================================================
print(f"\n{'='*60}")
print("TEST 5: DO FOLIOS CLUSTER BY PAIR PROFILE?")
print(f"{'='*60}")

# Build folio x pair matrix
all_pairs_list = sorted(set(line_pairs.values()),
                         key=lambda p: (STAGE_ORDER[p[0]], STAGE_ORDER[p[1]]))
folio_list = sorted([f for f in folio_pairs if len(folio_pairs[f]) >= 5])

folio_vectors = {}
for folio in folio_list:
    pair_counts = Counter(folio_pairs[folio])
    total = sum(pair_counts.values())
    vec = np.array([pair_counts.get(p, 0) / total for p in all_pairs_list])
    folio_vectors[folio] = vec

# Within-section vs between-section cosine similarity
within_cosines = []
between_cosines = []

folio_list_with_section = [(f, folio_sections.get(f, '?')) for f in folio_list]

for i in range(len(folio_list)):
    for j in range(i + 1, len(folio_list)):
        f1, s1 = folio_list_with_section[i]
        f2, s2 = folio_list_with_section[j]
        v1, v2 = folio_vectors[f1], folio_vectors[f2]
        dot = np.dot(v1, v2)
        norm = np.linalg.norm(v1) * np.linalg.norm(v2)
        cos_sim = dot / norm if norm > 0 else 0

        if s1 == s2:
            within_cosines.append(cos_sim)
        else:
            between_cosines.append(cos_sim)

within_mean = np.mean(within_cosines) if within_cosines else 0
between_mean = np.mean(between_cosines) if between_cosines else 0
section_lift = within_mean / between_mean if between_mean > 0 else 0

print(f"  Within-section folio similarity: {within_mean:.4f} (n={len(within_cosines)})")
print(f"  Between-section folio similarity: {between_mean:.4f} (n={len(between_cosines)})")
print(f"  Section clustering lift: {section_lift:.3f}x")

# ============================================================
# TEST 6: The operator's journey - trace one material state
# ============================================================
print(f"\n{'='*60}")
print("TEST 6: OPERATOR'S JOURNEY - TRACE ONE STATE")
print(f"{'='*60}")

# Pick the most common pair and show all folios that contain it
top_pair = Counter(line_pairs.values()).most_common(1)[0][0]
label = f"{top_pair[0][:4]}>{top_pair[1][:4]}"
print(f"\n  Most common pair: {label} ({pair_total_lines[top_pair]} lines)")
print(f"  Appears in {len(pair_folios[top_pair])} folios:")

# For each folio with this pair, show context
for folio in sorted(pair_folios[top_pair]):
    section = folio_sections.get(folio, '?')
    folio_total = len(folio_pairs[folio])
    pair_count = sum(1 for p in folio_pairs[folio] if p == top_pair)
    pct = pair_count / folio_total * 100

    # What other pairs share this folio?
    other_pairs = Counter(p for p in folio_pairs[folio] if p != top_pair)
    top_other = other_pairs.most_common(2)
    other_str = ', '.join(f"{p[0][:4]}>{p[1][:4]}({c})" for p, c in top_other)

    print(f"    {folio} (S={section}): {pair_count}/{folio_total} lines ({pct:.0f}%)  "
          f"also: {other_str}")

# ============================================================
# TEST 7: Could a single folio be a "complete manual" for one material?
# ============================================================
print(f"\n{'='*60}")
print("TEST 7: FOLIO GRID COVERAGE")
print(f"{'='*60}")

# How much of the 6x6 grid does each folio cover?
grid_size = len(STAGES) ** 2  # 36 possible cells

coverages = []
for folio in folio_list:
    pairs = set(folio_pairs[folio])
    coverage = len(pairs) / grid_size
    coverages.append(coverage)

print(f"  Mean folio grid coverage: {np.mean(coverages)*100:.1f}% of 36 cells")
print(f"  Max coverage: {max(coverages)*100:.1f}%")
print(f"  Min coverage: {min(coverages)*100:.1f}%")

# Show the best-covered folios
folio_coverages = [(f, len(set(folio_pairs[f])), len(folio_pairs[f]))
                    for f in folio_list]
folio_coverages.sort(key=lambda x: -x[1])

print(f"\n  Most diverse folios:")
for folio, unique, total in folio_coverages[:8]:
    section = folio_sections.get(folio, '?')
    print(f"    {folio} (S={section}): {unique} unique pairs from {total} lines "
          f"({unique/grid_size*100:.0f}% coverage)")

print(f"\n  Least diverse folios (with n>=5):")
for folio, unique, total in folio_coverages[-5:]:
    section = folio_sections.get(folio, '?')
    top_pair = Counter(folio_pairs[folio]).most_common(1)[0]
    print(f"    {folio} (S={section}): {unique} unique pairs from {total} lines, "
          f"top={top_pair[0][0][:4]}>{top_pair[0][1][:4]}({top_pair[1]})")

# ============================================================
# Verdict
# ============================================================
print(f"\n{'='*60}")
print("VERDICT: HOW DOES AN OPERATOR USE THIS?")
print(f"{'='*60}")

# Is it a dedicated-folio system (each folio covers few pairs)
# or a distributed system (each pair appears in many folios)?
mean_folios_per_pair = np.mean([len(pair_folios[p]) for p in pair_folios
                                if pair_total_lines[p] >= 10])
mean_pairs_per_folio = np.mean([len(set(folio_pairs[f])) for f in folio_list])

print(f"  Mean folios per pair: {mean_folios_per_pair:.1f}")
print(f"  Mean unique pairs per folio: {mean_pairs_per_folio:.1f}")
print(f"  Section clustering: {section_lift:.3f}x")
print(f"  Mean grid coverage per folio: {np.mean(coverages)*100:.1f}%")

if mean_folios_per_pair < 5 and mean_pairs_per_folio < 5:
    nav_model = "DEDICATED_FOLIOS"
    explanation = "Each folio specializes in a narrow pair range - flip to the right page"
elif section_lift > 1.3:
    nav_model = "SECTION_THEN_FOLIO"
    explanation = "Section narrows the search, then scan folios within section"
elif mean_pairs_per_folio > 8:
    nav_model = "DISTRIBUTED"
    explanation = "Each folio covers many states - the folio IS the procedure, FL tags are in-page navigation"
else:
    nav_model = "MIXED"
    explanation = "Moderate specialization - folios cluster by section but cover multiple states"

print(f"\n  NAVIGATION MODEL: {nav_model}")
print(f"  {explanation}")

# Save
result = {
    'n_lines_with_pairs': len(line_pairs),
    'n_folios': len(folio_pairs),
    'mean_diversity_per_folio': round(float(np.mean(folio_diversity)), 3),
    'mean_top_pair_coverage': round(float(np.mean(folio_top_pair_coverage)), 3),
    'mean_folios_per_pair': round(float(mean_folios_per_pair), 1),
    'mean_pairs_per_folio': round(float(mean_pairs_per_folio), 1),
    'section_clustering_lift': round(float(section_lift), 3),
    'mean_grid_coverage': round(float(np.mean(coverages)), 3),
    'nav_model': nav_model,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / "results" / "30_operator_navigation.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nResult written to {out_path}")
